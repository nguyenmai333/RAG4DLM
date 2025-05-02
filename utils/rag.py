import os 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from config import *
#--init--
# Create the client with persistence
client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

try:
    collection = client.get_collection(name="documents")
    if collection:
        client.delete_collection(name="documents")
except Exception:
    pass

# Create fresh collection
collection = client.create_collection(name="documents")

#--init--
def chunk_text(text, chunk_size = 100, overlap = 20):
    def word_count(s):
        return len(s.split())
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=word_count,
        separators=[" ", "", "\n", "\n\n", "\n\n\n"]
    )
    return text_splitter.split_text(text)

def load_documents(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                documents.append(content)
    return documents

def build_rag_system(documents, chunk_size=100, overlap = 20):
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc, chunk_size, overlap)
        all_chunks.extend(chunks)

    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = embedding_model.encode(all_chunks, show_progress_bar=True)
    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=[{"source": str(i)} for i in range(len(all_chunks))],
        ids=[str(i) for i in range(len(all_chunks))]
    )

if __name__ == "__main__":
    document_directory = 'docs'
    documents = load_documents(document_directory)
    build_rag_system(documents, chunk_size=100, overlap=20)

