"""
Minimal FastAPI test - to verify Railway works at all
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Minimal test API works!"}

@app.get("/health")
def health():
    return {"status": "healthy", "test": "minimal"}

