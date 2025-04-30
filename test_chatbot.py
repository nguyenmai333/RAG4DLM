import pytest
import pandas as pd
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from dotenv import load_dotenv
import os

load_dotenv()

def test_cases_from_csv(csv_path="test_queries_with_responses.csv", output_csv="metric_results.csv"):
    df = pd.read_csv(csv_path)
    
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5,
        model='gpt-4o-mini'
    )
    
    results = []
    
    for _, row in df.iterrows():
        test_case = LLMTestCase(
            input=row['query'],
            actual_output=row['rag_response'],
            expected_output=row['ground_truth'],
            retrieval_context=[row['ground_truth']]  
        )
        

        try:
            assert_test(test_case, [correctness_metric])
            result = {
                'query': row['query'],
                'actual_output': row['rag_response'],
                'expected_output': row['ground_truth'],
                'correctness_score': correctness_metric.score,
                'pass': True,
                'reason': 'Score above threshold'
            }
        except AssertionError as e:
            result = {
                'query': row['query'],
                'actual_output': row['rag_response'],
                'expected_output': row['ground_truth'],
                'correctness_score': correctness_metric.score if hasattr(correctness_metric, 'score') else 0.0,
                'pass': False,
                'reason': str(e)
            }
        
        results.append(result)
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    
    return results_df


def test_evaluate_csv():
    results = test_cases_from_csv()
    assert len(results) > 0, "No test cases were evaluated"
    assert results['pass'].all(), f"Some test cases failed: {results[~results['pass']]['reason'].tolist()}"

if __name__ == "__main__":
    pytest.main([__file__])