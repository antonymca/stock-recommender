from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Stock Recommender API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Stock Recommender API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/signals/{ticker}")
async def get_stock_signal(ticker: str):
    # Placeholder implementation
    return {
        "ticker": ticker.upper(),
        "signal": "BUY",
        "score": 0.75,
        "price": 150.25,
        "reason": "Strong technical indicators and positive momentum"
    }