import pickle
import pandas as pd

df = pickle.load(open("catalog.pkl", "rb"))

print(df["test_type"].value_counts())