import json
from typing import List
from difflib import SequenceMatcher

def load_ground_truth(file_path: str) -> List[dict]:
    """
    Load ground truth data from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_similarity(expected: str, generated: str) -> float:
    """
    Calculate similarity between two strings using SequenceMatcher.
    """
    return SequenceMatcher(None, expected, generated).ratio()

def evaluate_responses(ground_truth_data: List[dict]):
    """
    Evaluate generated responses against expected responses.
    """
    evaluation_results = []

    for item in ground_truth_data:
        query = item["query"]
        expected_response = item["expected_response"]
        generated_response = item["generated_response"]

        similarity_score = calculate_similarity(expected_response, generated_response)

        evaluation_results.append({
            "query": query,
            "expected_response": expected_response,
            "generated_response": generated_response,
            "similarity_score": similarity_score
        })

    return evaluation_results

def save_evaluation_results_to_file(data: List[dict], file_path: str):
    """
    Save evaluation results to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    print("Loading ground truth data...")
    ground_truth_data = load_ground_truth("ground_truth.json")

    print("Evaluating responses...")
    evaluation_results = evaluate_responses(ground_truth_data)

    print("Saving evaluation results...")
    save_evaluation_results_to_file(evaluation_results, "evaluation_results.json")

    print("Evaluation complete. Results saved to 'evaluation_results.json'")