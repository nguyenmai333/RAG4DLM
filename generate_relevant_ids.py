# generate_relevant_ids.py
import pandas as pd
from utils.query import retrive_documents_with_metadata
import json

test_data = pd.read_csv("test_queries.csv")
relevant_doc_ids = {}

for idx, row in test_data.iterrows():
    query = row["query"]
    _, metadatas = retrive_documents_with_metadata(query, k=2)  # Get top-2 documents
    relevant_ids = [meta["source"] for meta in metadatas[0]]  # Assume top-2 are relevant
    relevant_doc_ids[idx] = relevant_ids

with open("relevant_doc_ids.json", "w") as f:
    json.dump(relevant_doc_ids, f)