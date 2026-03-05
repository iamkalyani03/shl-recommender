# recommender.py

import faiss
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from llm_processor import extract_requirements

INDEX_FILE = "shl_index.faiss"
METADATA_FILE = "catalog.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 10

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")
index = faiss.read_index(INDEX_FILE)

print("Loading metadata...")
df = pickle.load(open(METADATA_FILE, "rb"))


# --------------------------------------------------
# SMART BALANCING
# --------------------------------------------------
def balanced_filter(results_df, top_k=10):

    k_tests = results_df[results_df["test_type"] == "K"]
    p_tests = results_df[results_df["test_type"] == "P"]

    half = top_k // 2

    selected_k = k_tests.head(half)
    selected_p = p_tests.head(half)

    combined = pd.concat([selected_k, selected_p])

    if len(combined) < top_k:
        remaining = results_df[~results_df.index.isin(combined.index)]
        combined = pd.concat([combined, remaining.head(top_k - len(combined))])

    return combined.head(top_k)


def search(query, top_k=10):

    requirements = extract_requirements(query)

    technical = " ".join(requirements["technical_skills"])
    behavioral = " ".join(requirements["behavioral_skills"])
    role = requirements["role_type"]

    enriched_query = f"{query} {technical} {behavioral} {role}"

    # 🔹 Technical semantic search
    query_embedding = model.encode(
        [enriched_query],
        normalize_embeddings=True
    )

    scores, indices = index.search(
        np.array(query_embedding),
        top_k * 5
    )

    results_df = df.iloc[indices[0]].copy()
    results_df["score"] = scores[0]

    results_df = results_df.sort_values(
        by="score",
        ascending=False
    )

    # 🔥 If behavioral skills exist, force include top personality tests
    if behavioral:

        personality_pool = df[df["test_type"] == "P"].copy()

        personality_embedding = model.encode(
            [behavioral],
            normalize_embeddings=True
        )

        p_scores, p_indices = index.search(
            np.array(personality_embedding),
            top_k
        )

        p_results = df.iloc[p_indices[0]].copy()
        p_results["score"] = p_scores[0]

        results_df = pd.concat([results_df, p_results])

        results_df = results_df.drop_duplicates(subset=["URL"])

        results_df = results_df.sort_values(
            by="score",
            ascending=False
        )

    return results_df.head(top_k)[[
        "Product Name",
        "URL",
        "Description",
        "test_type",
        "score"
    ]]