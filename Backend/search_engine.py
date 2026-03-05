import faiss
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# ==============================
# SETTINGS
# ==============================

INDEX_FILE = "shl_index.faiss"
METADATA_FILE = "catalog.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 10

# ==============================
# LOAD MODEL + INDEX
# ==============================

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")
index = faiss.read_index(INDEX_FILE)

print("Loading metadata...")
df = pickle.load(open(METADATA_FILE, "rb"))

# ==============================
# BALANCED FILTER (K/P Split)
# ==============================

def balanced_filter(results_df, top_k=10):
    """
    Ensure mix of Knowledge (K) and Personality (P) tests.
    """

    k_tests = results_df[results_df["test_type"] == "K"]
    p_tests = results_df[results_df["test_type"] == "P"]

    half = top_k // 2

    final = pd.concat([
        k_tests.head(half),
        p_tests.head(half)
    ])

    # If not enough K/P, fallback to similarity ranking
    if len(final) < top_k:
        final = results_df.head(top_k)

    return final


# ==============================
# SEARCH FUNCTION
# ==============================

def search(query, top_k=TOP_K, balanced=True):

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    results_df = df.iloc[indices[0]].copy()
    results_df["score"] = scores[0]

    # Sort by similarity score
    results_df = results_df.sort_values(
        by="score",
        ascending=False
    )

    if balanced:
        results_df = balanced_filter(results_df, top_k)

    return results_df[[
        "Product Name",
        "URL",
        "Description",
        "test_type",
        "score"
    ]]


# ==============================
# CLI LOOP
# ==============================

if __name__ == "__main__":

    while True:
        user_query = input("\nEnter search query (or 'exit'): ")

        if user_query.lower() == "exit":
            break

        results = search(user_query)

        print("\nTop Recommendations:\n")

        for i, (_, row) in enumerate(results.iterrows(), 1):
            print(f"{i}. {row['Product Name']}")
            print(f"   Type: {row['test_type']}")
            print(f"   Score: {row['score']:.4f}")
            print(f"   URL: {row['URL']}")
            print()