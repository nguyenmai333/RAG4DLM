from utils.query import *
import pandas as pd

path_ = "test_queries.csv"

df = pd.read_csv(path_)

df['rag_response'] = ''

for idx, row in df.iterrows():
    response = retrive_documents(row['query'])
    df.at[idx, 'rag_response'] = response

df.to_csv('test_queries_with_responses.csv', index=False)