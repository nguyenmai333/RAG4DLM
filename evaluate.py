import pandas as pd
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from sentence_transformers import SentenceTransformer, util
import time
from utils.query import retrive_documents, retrive_documents_with_metadata
from utils.llm_grok import GrokLLM
from utils.llm_deepseek import DeepseekLLM
from utils.llm_openai import OpenAILLM
from utils.config import *
import os
from dotenv import load_dotenv
import json
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from underthesea import word_tokenize

nltk.download("punkt", quiet=True)

with open("relevant_doc_ids.json", "r") as f:
    relevant_doc_ids = json.load(f)

load_dotenv()

# Initialize models
models = {
    "Grok": GrokLLM(model_name="grok-3-mini-latest", api_key=os.getenv("GROK_API_KEY")),
    "DeepSeek": DeepseekLLM(model_name="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY")),
    "OpenAI": OpenAILLM(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
}

# Load embedding model for semantic similarity
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Load test queries
test_data = pd.read_csv("test_queries.csv")

# Ground truth for document relevance (manually curated or inferred)
# Example: relevant_doc_ids maps query index to list of relevant document IDs
relevant_doc_ids = {
    # Populate manually or via preprocessing
    # e.g., 0: ["0", "1"], 1: ["3", "4"] for query 0 and 1
}

# Initialize results storage
results = []

def compute_retrieval_metrics(documents, metadatas, relevant_ids, k=2):
    retrieved_ids = [meta["source"] for meta in metadatas[0]]
    relevant_retrieved = [doc_id for doc_id in retrieved_ids if doc_id in relevant_ids]
    
    # Precision@K
    precision = len(relevant_retrieved) / k if k > 0 else 0
    
    # Recall@K
    total_relevant = len(relevant_ids)
    recall = len(relevant_retrieved) / total_relevant if total_relevant > 0 else 0
    
    # MRR
    mrr = 0
    for i, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_ids:
            mrr = 1 / i
            break
    
    return precision, recall, mrr

def compute_response_metrics(response, ground_truth):
    # Tokenize Vietnamese text
    response_tokens = word_tokenize(response)
    ground_truth_tokens = word_tokenize(ground_truth)
    
    # BLEU with smoothing and custom weights
    smoothie = SmoothingFunction().method1
    bleu = sentence_bleu([ground_truth_tokens], response_tokens, 
                         weights=(0.5, 0.3, 0.2, 0.0), 
                         smoothing_function=smoothie)
    
    # ROUGE
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    rouge_scores = scorer.score(ground_truth, response)
    rouge_l = rouge_scores['rougeL'].fmeasure
    
    # Semantic Similarity
    response_embedding = embedding_model.encode(response)
    gt_embedding = embedding_model.encode(ground_truth)
    semantic_sim = util.cos_sim(response_embedding, gt_embedding).item()
    
    return bleu, rouge_l, semantic_sim

def evaluate_model(model_name, llm, query, ground_truth, relevant_ids):
    start_time = time.perf_counter()
    documents, metadatas = retrive_documents_with_metadata(query, k=2)
    full_response = ""
    for chunk in llm.streaming_answer(query):
        full_response += chunk or ""
    response_time = time.perf_counter() - start_time
    
    # Log response for debugging
    # print(f"Query: {query}")
    # print(f"Response: {full_response}")
    # print(f"Ground Truth: {ground_truth}")
    # print("-" * 50)
    
    precision, recall, mrr = compute_retrieval_metrics(documents, metadatas, relevant_ids)
    bleu, rouge_l, semantic_sim = compute_response_metrics(full_response, ground_truth)
    factual_accuracy = None
    
    return {
        "model": model_name,
        "query": query,
        "response": full_response,
        "ground_truth": ground_truth,
        "precision@2": precision,
        "recall@2": recall,
        "mrr": mrr,
        "bleu": bleu,
        "rouge_l": rouge_l,
        "semantic_similarity": semantic_sim,
        "response_time": response_time,
        "factual_accuracy": factual_accuracy
    }

# Main evaluation loop
for idx, row in test_data.iterrows():
    query = row["query"]
    ground_truth = row["ground_truth"]
    relevant_ids = relevant_doc_ids.get(idx, [])  # Get relevant document IDs for this query
    
    for model_name, llm in models.items():
        try:
            result = evaluate_model(model_name, llm, query, ground_truth, relevant_ids)
            results.append(result)
        except Exception as e:
            print(f"Error evaluating {model_name} for query {query}: {str(e)}")

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv("evaluation_results.csv", index=False)

# Aggregate metrics
summary = results_df.groupby("model").agg({
    "precision@2": "mean",
    "recall@2": "mean",
    "mrr": "mean",
    "bleu": "mean",
    "rouge_l": "mean",
    "semantic_similarity": "mean",
    "response_time": "mean"
}).reset_index()

print("Evaluation Summary:")
print(summary)

# Save summary to CSV
summary.to_csv("evaluation_summary.csv", index=False)