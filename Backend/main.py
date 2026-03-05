from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommender import search

app = FastAPI(title="SHL Assessment Recommendation API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins, or replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],        # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],        # Allow all headers
)

# Request schema
class QueryRequest(BaseModel):
    query: str
    top_k: int = 10

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "API is running"}

# Recommendation endpoint
@app.post("/recommend")
def recommend(req: QueryRequest):
    results = search(req.query, top_k=req.top_k)
    output = [
        {
            "assessment_name": r["Product Name"],
            "assessment_url": r["URL"],
            "score": float(r["score"])
        } 
        for _, r in results.iterrows()
    ]
    return {"query": req.query, "recommendations": output}

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)