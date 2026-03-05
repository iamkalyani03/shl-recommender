import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ==========================================
# SETTINGS
# ==========================================

CSV_FILE = "shl_product_catalog_cleaned.csv"
INDEX_FILE = "shl_index.faiss"
METADATA_FILE = "catalog.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# ==========================================
# LOAD CSV
# ==========================================

print("Loading catalog CSV...")
df = pd.read_csv(CSV_FILE)

# Clean missing values
df = df.fillna("")

# ==========================================
# INFER TEST TYPE (K = Knowledge, P = Personality)
# ==========================================

def infer_test_type(text):
    text = text.lower()

    knowledge_keywords = [
        "knowledge", "multi-choice", "technical",
        "programming", "chemistry", "linux",
        ".net", "framework", "administration",
        "system", "wpf", "xaml"
    ]

    personality_keywords = [
        "behavior", "personality", "leadership",
        "supervisor", "solution", "entry level",
        "communication", "sales", "fluency",
        "spoken", "writing", "customer service",
        "manager", "teller"
    ]

    for word in knowledge_keywords:
        if word in text:
            return "K"

    for word in personality_keywords:
        if word in text:
            return "P"

    return "K"  # default fallback


print("Inferring test types (K/P)...")
df["combined_text"] = (
    df["Product Name"].astype(str) + " " +
    df["Description"].astype(str)
)

df["test_type"] = df["combined_text"].apply(infer_test_type)

# ==========================================
# GENERATE EMBEDDINGS
# ==========================================

print("Generating embeddings...")

texts = df["combined_text"].tolist()

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True  # Important for cosine similarity
)

# ==========================================
# BUILD FAISS INDEX (Cosine Similarity)
# ==========================================

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine
index.add(embeddings)

print("Total vectors in index:", index.ntotal)

# ==========================================
# SAVE FILES
# ==========================================

faiss.write_index(index, INDEX_FILE)
df.to_pickle(METADATA_FILE)

print("\n STEP 2 COMPLETE — Embeddings + FAISS index created!")
print(" Files saved:")
print("  -", INDEX_FILE)
print("  -", METADATA_FILE)