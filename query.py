from config import *
import os
import chroma_db
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from transformers import T5ForConditionalGeneration, T5Tokenizer

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection(name="documents")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def retrive_documents(query, k = 2):
    # Perform the queryODEL)
    query_embedding = embedding_model.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2,
        include=["documents", "metadatas", "distances"]
    )
    return results['documents'][0]

if __name__ == "__main__":
    while True:
        query = input("Enter your query: ")
        if query.lower() == 'exit':
            break
        # Perform the query
        results = retrive_documents(query = query, k = 2)
        print("Results:", results)