from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import yfinance as yf
import pandas as pd
from tensorflow.keras.models import load_model
import os

app = FastAPI(
    title="StockMind AI",
    description="LSTM-powered stock price prediction API",
    version="1.0.0"
)

# ── CORS — allows frontend to call this API 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE_DIR, 'models', 'best_model.keras')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')

# ── Load model & scaler once at startup 
print("Loading model and scaler...")
model  = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
print("Ready ✅")


# ── Pydantic response models ───────

class HealthResponse(BaseModel):
    status: str
    message: str

class PredictionResponse(BaseModel):
    ticker: str
    current_price: float
    predicted_price: float
    change: float
    change_pct: float

class HistoryResponse(BaseModel):
    ticker: str
    dates: list[str]
    prices: list[float]
    prediction: float


# ── Helper: fetch & prepare latest data ───
def get_latest_data(ticker: str, window: int = 60):
    """
    Fetch recent data and prepare sequence for prediction.
    Returns normalized sequence + raw closes.
    """
    df = yf.download(ticker, period="6mo", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < window:
        return None, None

    closes        = df['Close'].values.reshape(-1, 1)
    closes_scaled = scaler.transform(closes)
    sequence      = closes_scaled[-window:].reshape(1, window, 1)

    return sequence, closes


# ── 1. Health check────
@app.get("/api/health", response_model=HealthResponse)
def health():
    """Check if the API is running."""
    return {
        "status": "ok",
        "message": "StockMind API is running"
    }


# ── 2. Predict next day price ───────────────────────────
@app.get("/api/predict", response_model=PredictionResponse)
def predict(
    ticker: str = Query(default="AAPL", description="Stock ticker symbol e.g. AAPL")
):
    """
    Predict the next trading day's closing price for a given ticker.
    """
    ticker   = ticker.upper()
    sequence, closes = get_latest_data(ticker)

    if sequence is None:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data for ticker '{ticker}'. Check the symbol."
        )

    # Predict
    pred_scaled = model.predict(sequence, verbose=0)
    pred_price  = float(scaler.inverse_transform(pred_scaled)[0][0])

    current_price = float(closes[-1][0])
    change        = pred_price - current_price
    change_pct    = (change / current_price) * 100

    return {
        "ticker"          : ticker,
        "current_price"   : round(current_price, 2),
        "predicted_price" : round(pred_price, 2),
        "change"          : round(change, 2),
        "change_pct"      : round(change_pct, 2)
    }


# ── 3. Historical prices + prediction ───────────────────
@app.get("/api/history", response_model=HistoryResponse)
def history(
    ticker: str = Query(default="AAPL", description="Stock ticker symbol"),
    days  : int = Query(default=90,     description="Number of historical days to return")
):
    """
    Return historical closing prices and next day prediction.
    """
    ticker = ticker.upper()

    df = yf.download(ticker, period="1y", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < 60:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data for ticker '{ticker}'"
        )

    recent = df['Close'].tail(days)
    dates  = [str(d.date()) for d in recent.index]
    prices = [round(float(p), 2) for p in recent.values]

    # Next day prediction
    sequence, _  = get_latest_data(ticker)
    pred_scaled  = model.predict(sequence, verbose=0)
    pred_price   = float(scaler.inverse_transform(pred_scaled)[0][0])

    return {
        "ticker"    : ticker,
        "dates"     : dates,
        "prices"    : prices,
        "prediction": round(pred_price, 2)
    }


# ── 4. Compare multiple tickers ─────────────────────────
@app.get("/api/compare")
def compare(
    tickers: str = Query(default="AAPL,MSFT,GOOGL", description="Comma separated tickers")
):
    """
    Predict next day price for multiple tickers at once.
    Example: /api/compare?tickers=AAPL,MSFT,TSLA
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results     = []

    for ticker in ticker_list:
        sequence, closes = get_latest_data(ticker)

        if sequence is None:
            results.append({"ticker": ticker, "error": "Not enough data"})
            continue

        pred_scaled   = model.predict(sequence, verbose=0)
        pred_price    = float(scaler.inverse_transform(pred_scaled)[0][0])
        current_price = float(closes[-1][0])
        change_pct    = ((pred_price - current_price) / current_price) * 100

        results.append({
            "ticker"          : ticker,
            "current_price"   : round(current_price, 2),
            "predicted_price" : round(pred_price, 2),
            "change_pct"      : round(change_pct, 2)
        })

    return {"comparisons": results}