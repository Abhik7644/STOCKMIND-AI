from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import yfinance as yf
import pandas as pd
import os

# ── Database + Auth imports ──────────────────────────────
from src.database import create_db_tables
from src.auth.router import router as auth_router

# ── Multi-stock predict imports ──────────────────────────
from src.predict import load_model_and_scaler, model_exists
from src.data_loader import fetch_stock_data
from src.preprocessor import preprocess_pipeline
from src.train import train_model

# ── App setup ────────────────────────────────────────────
app = FastAPI(
    title="StockMind AI",
    description="LSTM-powered stock price prediction API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ─────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR   = os.path.join(BASE_DIR, 'data')


# ── Startup ───────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_db_tables()
    print("Database tables created ✅")


# ── Register auth routes ──────────────────────────────────
app.include_router(auth_router)


# ── Response models ───────────────────────────────────────
class HealthResponse(BaseModel):
    status : str
    message: str

class PredictionResponse(BaseModel):
    ticker          : str
    current_price   : float
    predicted_price : float
    change          : float
    change_pct      : float
    model_status    : str   # 'pretrained' or 'trained_on_demand'

class HistoryResponse(BaseModel):
    ticker    : str
    dates     : List[str]
    prices    : List[float]
    prediction: float


# ── Helper: get latest data using ticker-specific scaler ──
def get_latest_data(ticker: str, window: int = 60):
    """
    Fetch recent prices and normalize using
    the ticker's own scaler.
    """
    # Load this ticker's scaler
    _, scaler = load_model_and_scaler(ticker, MODELS_DIR)

    df = yf.download(ticker, period="6mo", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < window:
        return None, None

    closes        = df['Close'].values.reshape(-1, 1)
    closes_scaled = scaler.transform(closes)
    sequence      = closes_scaled[-window:].reshape(1, window, 1)

    return sequence, closes


# ── Helper: train on demand if model doesn't exist ────────
def ensure_model_exists(ticker: str):
    """
    Check if model exists for ticker.
    If not — fetch data and train one automatically.
    Returns 'pretrained' or 'trained_on_demand'
    """
    if model_exists(ticker, MODELS_DIR):
        return 'pretrained'

    print(f"No model for {ticker} — training on demand...")

    df = fetch_stock_data(
        ticker,
        start='2019-01-01',
        end='2024-01-01',
        save_path=os.path.join(DATA_DIR, f"{ticker}_raw.csv")
    )

    X_train, _, y_train, _, _ = preprocess_pipeline(
        df,
        ticker=ticker,
        models_dir=MODELS_DIR,
        save_dir=DATA_DIR
    )

    train_model(X_train, y_train, ticker=ticker, models_dir=MODELS_DIR)

    print(f"✅ {ticker} model trained and saved!")
    return 'trained_on_demand'


# ════════════════════════════════════════════════════════
#  ROUTES
# ════════════════════════════════════════════════════════

# ── 1. Health check ───────────────────────────────────────
@app.get("/api/health", response_model=HealthResponse)
def health():
    return {
        "status" : "ok",
        "message": "StockMind API v2.0 is running"
    }


# ── 2. Predict next day price ─────────────────────────────
@app.get("/api/predict", response_model=PredictionResponse)
def predict(
    ticker: str = Query(default="AAPL",
                        description="Stock ticker e.g. AAPL")
):
    """
    Predict next trading day closing price.
    Auto-trains model if ticker not in pre-trained list.
    """
    ticker = ticker.upper()

    # Train on demand if needed
    model_status = ensure_model_exists(ticker)

    # Load this ticker's model + scaler
    model, scaler = load_model_and_scaler(ticker, MODELS_DIR)

    sequence, closes = get_latest_data(ticker)
    if sequence is None:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data for '{ticker}'"
        )

    pred_scaled   = model.predict(sequence, verbose=0)
    pred_price    = float(scaler.inverse_transform(pred_scaled)[0][0])
    current_price = float(closes[-1][0])
    change        = pred_price - current_price
    change_pct    = (change / current_price) * 100

    return {
        "ticker"          : ticker,
        "current_price"   : round(current_price, 2),
        "predicted_price" : round(pred_price, 2),
        "change"          : round(change, 2),
        "change_pct"      : round(change_pct, 2),
        "model_status"    : model_status
    }


# ── 3. Historical prices + prediction ─────────────────────
@app.get("/api/history", response_model=HistoryResponse)
def history(
    ticker: str = Query(default="AAPL"),
    days  : int = Query(default=90)
):
    """Return historical prices + next day prediction."""
    ticker = ticker.upper()

    ensure_model_exists(ticker)

    df = yf.download(ticker, period="1y", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < 60:
        raise HTTPException(status_code=400,
                            detail=f"Not enough data for '{ticker}'")

    recent = df['Close'].tail(days)
    dates  = [str(d.date()) for d in recent.index]
    prices = [round(float(p), 2) for p in recent.values]

    model, scaler = load_model_and_scaler(ticker, MODELS_DIR)
    sequence, _   = get_latest_data(ticker)
    pred_scaled   = model.predict(sequence, verbose=0)
    pred_price    = float(scaler.inverse_transform(pred_scaled)[0][0])

    return {
        "ticker"    : ticker,
        "dates"     : dates,
        "prices"    : prices,
        "prediction": round(pred_price, 2)
    }


# ── 4. Compare multiple tickers ───────────────────────────
@app.get("/api/compare")
def compare(
    tickers: str = Query(
        default="AAPL,MSFT,GOOGL,TSLA",
        description="Comma separated tickers"
    )
):
    """Predict next day price for multiple tickers."""
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results     = []

    for ticker in ticker_list:
        try:
            ensure_model_exists(ticker)
            model, scaler = load_model_and_scaler(ticker, MODELS_DIR)
            sequence, closes = get_latest_data(ticker)

            if sequence is None:
                results.append({"ticker": ticker, "error": "Not enough data"})
                continue

            pred_scaled   = model.predict(sequence, verbose=0)
            pred_price    = float(scaler.inverse_transform(pred_scaled)[0][0])
            current_price = float(closes[-1][0])
            change_pct    = ((pred_price - current_price) / current_price) * 100

            results.append({
                "ticker"         : ticker,
                "current_price"  : round(current_price, 2),
                "predicted_price": round(pred_price, 2),
                "change_pct"     : round(change_pct, 2)
            })

        except Exception as e:
            results.append({"ticker": ticker, "error": str(e)})

    return {"comparisons": results}