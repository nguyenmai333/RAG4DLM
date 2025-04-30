from sentence_transformers import SentenceTransformer
import chromadb
from .config import *

client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = client.get_collection(name="documents")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def retrive_documents(query, k=2):
    query_embedding = embedding_model.encode([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    return results['documents'][0]  # original behavior for chatbot

# if __name__ == "__main__":
#     while True:
#         query = input("Enter your query: ")
#         if query.lower() == 'exit':
#             break
#         results = retrive_documents(query=query, k=2)
#         print("Results:", results)