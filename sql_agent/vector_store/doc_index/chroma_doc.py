import chromadb
import os
import glob
from tqdm import tqdm
from typing import List
from multiprocessing import Pool
from sql_agent.config import System
from overrides import override
from sql_agent.vector_store.doc_index import DocIndex
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

chunk_size = 500
chunk_overlap = 50


class MyElmLoader(UnstructuredEmailLoader):
    def load(self) -> List[Document]:
        try:
            try:
                doc = UnstructuredEmailLoader.load(self)
            except ValueError as e:
                if 'text/html content not found in email' in str(e):
                    # Try plain text
                    self.unstructured_kwargs["content_source"] = "text/plain"
                    doc = UnstructuredEmailLoader.load(self)
                else:
                    raise
        except Exception as e:
            # Add file_path to exception message
            raise type(e)(f"{self.file_path}: {e}") from e

        return doc


LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    # ".docx": (Docx2txtLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (MyElmLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PDFMinerLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_single_file(file_path, ignored_files):
    filtered_files = []
    if file_path not in ignored_files:
        filtered_files.append(file_path)
    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()
    return results


def process_single_doc(file_path: str,
                       ignored_files=None) -> List[Document]:
    if ignored_files is None:
        ignored_files = []
    docs = load_single_file(file_path, ignored_files)
    texts = []
    if not docs:
        return texts
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(docs)
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts


def does_vector_store_exist(persist_directory: str) -> bool:
    if os.path.exists(os.path.join(persist_directory, 'index')):
        if os.path.exists(os.path.join(persist_directory, 'chroma-collections.parquet')) and os.path.exists(
                os.path.join(persist_directory, 'chroma-embeddings.parquet')):
            list_index_files = glob.glob(os.path.join(persist_directory, 'index/*.bin'))
            list_index_files += glob.glob(os.path.join(persist_directory, 'index/*.pkl'))
            # At least 3 documents are needed in a working vectorstore
            if len(list_index_files) > 3:
                return True
    return False


class ChromaDoc(DocIndex):
    def __init__(self, system: System):
        super().__init__(system)
        self.csv_file_suffix = '_knowledge.csv'
        self.persist_directory = system.settings.persist_directory
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        self.embeddings = HuggingFaceEmbeddings(model_name=system.settings.embeddings_model_name)

    @override
    def query_doc(self, query_texts: str,
                  source: List[str],
                  collection: str,
                  num_results: int):
        db = Chroma(embedding_function=self.embeddings,
                    client=self.chroma_client,
                    collection_name=collection)
        if source:
            source = [item.replace('.csv', self.csv_file_suffix) for item in source]
            return db.similarity_search(query=query_texts, k=10, metadata_query={'source': source})
        else:
            return db.similarity_search_with_score(query_texts, k=10)

    @override
    def upload_doc(self, file_path: str, collection: str):
        if does_vector_store_exist(self.persist_directory):
            db = Chroma(client=self.chroma_client, embedding_function=self.embeddings, collection_name=collection)
            texts = process_single_doc(file_path, [metadata['source'] for metadata in collection['metadatas']])
            if texts:
                print(f"Creating embeddings. May take some minutes...")
            return db.add_documents(texts)

        else:
            print("Creating new vectorstore")
            texts = process_single_doc(file_path)
            if texts:
                print(f"Creating embeddings. May take some minutes...")
                db = Chroma(client=self.chroma_client, embedding_function=self.embeddings, collection_name=collection)
                return db.add_documents(texts)

    @override
    def delete_doc(self, ids: List[str],
                   collection: str) -> bool:
        target_collection = self.chroma_client.get_or_create_collection(collection)
        target_collection.delete(ids=ids)
        return True
