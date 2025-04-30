# inspect_chroma.py
import chromadb
from utils.config import PERSIST_DIRECTORY

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection("documents")
all_docs = collection.get(include=["documents", "metadatas"])

for doc_id, doc_content in zip(all_docs["ids"], all_docs["documents"]):
    print(f"ID: {doc_id}, Content: {doc_content[:100]}...")