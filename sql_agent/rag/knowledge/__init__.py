import logging
from abc import ABC, abstractmethod

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
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

from sql_agent.rag.knowledge.types import Document
from sql_agent.setting import System

logger = logging.getLogger(__name__)
chunk_size = 500
chunk_overlap = 50

KNOWLEDGE_EMBEDDING_COLLECTION = "knowledge_embedding"

system = System()


class MyElmLoader(UnstructuredEmailLoader):
    def load(self) -> list[Document]:
        try:
            try:
                doc = UnstructuredEmailLoader.load(self)
            except ValueError as e:
                if "text/html content not found in email" in str(e):
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


def load_single_document(file_path: str) -> list[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        logger.info(f"加载文件类型:{ext}")
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        logger.info(f"开始加载文件:{file_path}")
        docs = loader.load()
        logger.info(f"加载文件完成:{file_path}")
        return docs

    raise ValueError(f"Unsupported file extension '{ext}'")


def process_single_doc(file_path: str) -> list[Document]:
    docs = load_single_document(file_path)
    texts = []
    if not docs:
        return texts

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    logger.info(f"开始切分文件:{file_path}")
    texts = text_splitter.split_documents(docs)
    logger.info(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts


class KnowledgeService(ABC):
    collections: list[str]

    def __init__(self):
        self.system = system

    @abstractmethod
    def query_doc(self, query_texts: str, source: list[str], num_results: int):
        pass

    @abstractmethod
    def upload_doc(self, file_path: str, record_id: str):
        pass

    @abstractmethod
    def delete_doc(self, condition: dict):
        pass

    @abstractmethod
    def delete_doc_ids(self, ids: list[str]):
        pass
