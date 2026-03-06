import requests
import csv

TEST_QUERIES = [
    "Need Java developer with collaboration skills",
    "Looking to hire mid-level professionals proficient in Python, SQL and JavaScript",
    "Hiring an analyst, want Cognitive and Personality tests",
    "Frontend developer skilled in React and UX/UI design",
    "Customer service manager with leadership experience",
    "Data scientist with machine learning expertise",
    "Sales representative fluent in English and negotiation skills",
    "Team leader for software engineering projects",
    "Entry level IT support with problem-solving skills"
]

API_URL = "http://127.0.0.1:8000/recommend"
CSV_FILE = "shl_test_predictions.csv"

results = {}
for query in TEST_QUERIES:
    resp = requests.post(API_URL, json={"query": query, "top_k": 10})
    data = resp.json()
    results[query] = data["recommendations"]

with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Query","Assessment_url"])
    for query,recs in results.items():
        for rec in recs:
            writer.writerow([query, rec["assessment_url"]])

print(f"CSV generated: {CSV_FILE}")