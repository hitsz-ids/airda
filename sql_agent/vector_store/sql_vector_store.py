import json
import os
import chromadb
from typing import List, Union
from langchain.vectorstores import Chroma
from bson.objectid import ObjectId
from langchain.embeddings import HuggingFaceEmbeddings
from sql_agent.db.models.types import GoldenRecord
from dotenv import load_dotenv
from sql_agent.db.models.types import NlQuestion

load_dotenv('../../config.env')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME')
persist_directory = os.environ.get('PERSIST_DIRECTORY')

client = chromadb.PersistentClient(path=persist_directory)
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
sql_collection = 'golden_sql_collection'


def convert_to_object_model(chroma_results: dict) -> List:
    results = []
    for i in range(len(chroma_results["ids"][0])):
        results.append(
            {
                "id": chroma_results["ids"][0][i],
                "score": chroma_results["distances"][0][i],
            }
        )
    return results


def find_by_id(self, id: str) -> Union[GoldenRecord, None]:
    row = self.storage.find_one(sql_collection, {"_id": ObjectId(id)})
    if not row:
        return None
    row["id"] = str(row["_id"])
    row["db_connection_id"] = str(row["db_connection_id"])
    return GoldenRecord(**row)


def query(
        query_texts: List[str],
        db_connection_id: str,
        collection: str,
        num_results: int,
) -> list:
    try:
        target_collection = client.get_collection(collection)
    except ValueError:
        return []

    query_results = target_collection.query(
        query_texts=query_texts,
        n_results=num_results,
    )
    return convert_to_object_model(query_results)


def get_golden_sql(question: str, number_of_samples: int = 3):
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=sql_collection)
    docs = db.similarity_search(question, k=number_of_samples)
    golden_sql = ''
    for doc in docs:
        json_str = doc.page_content
        gold_record = json.loads(json_str)
        golden_sql += f"Question: {gold_record['nl_question']} -> SQL: {gold_record['sql_query']}\n"
    return golden_sql


def add_golden_sql(golden_sql: List[NlQuestion]):
    for sql in golden_sql:
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=sql_collection)
        print(123)