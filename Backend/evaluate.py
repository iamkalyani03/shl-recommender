# evaluate.py

import pandas as pd
from recommender import search

TRAIN_FILE = "train.csv"

train_df = pd.read_csv(TRAIN_FILE)


def recall_at_k(predicted_urls, actual_urls, k=10):
    predicted_k = predicted_urls[:k]
    relevant = set(actual_urls)
    return len(set(predicted_k) & relevant) / len(relevant)


recalls = []

for query, group in train_df.groupby("Query"):

    actual_urls = group["Assessment_url"].tolist()

    results = search(query, top_k=10)
    predicted_urls = results["URL"].tolist()

    score = recall_at_k(predicted_urls, actual_urls)
    recalls.append(score)

    print(f"Query: {query}")
    print("Recall@10:", score)
    print("-" * 50)

mean_recall = sum(recalls) / len(recalls)
print("\nFINAL Mean Recall@10:", mean_recall)