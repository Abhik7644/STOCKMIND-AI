import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"


# ── Core fetch function ───────────────────────────────────
def fetch_av(params: dict) -> dict:
    """Base function for all Alpha Vantage API calls."""
    params["apikey"] = API_KEY
    response = requests.get(BASE_URL, params=params)
    return response.json()


# ── RSI ───────────────────────────────────────────────────
def get_rsi(ticker: str) -> dict:
    """
    Fetch RSI (Relative Strength Index) for a ticker.
    RSI < 30 = Oversold (Bullish signal)
    RSI > 70 = Overbought (Bearish signal)
    30-70    = Neutral
    """
    data = fetch_av({
        "function"   : "RSI",
        "symbol"     : ticker,
        "interval"   : "daily",
        "time_period": 14,
        "series_type": "close"
    })

    if "Technical Analysis: RSI" not in data:
        return {"error": "RSI data unavailable", "value": None}

    # Get most recent RSI value
    rsi_data   = data["Technical Analysis: RSI"]
    latest_date = sorted(rsi_data.keys())[-1]
    rsi_value   = float(rsi_data[latest_date]["RSI"])

    # Generate signal
    if rsi_value < 30:
        signal    = "Bullish"
        signal_msg= "Stock appears oversold — potential buying opportunity"
        color     = "green"
    elif rsi_value > 70:
        signal    = "Bearish"
        signal_msg= "Stock appears overbought — potential selling pressure"
        color     = "red"
    else:
        signal    = "Neutral"
        signal_msg= "Stock is trading in normal range"
        color     = "yellow"

    return {
        "ticker"    : ticker,
        "rsi"       : round(rsi_value, 2),
        "signal"    : signal,
        "message"   : signal_msg,
        "color"     : color,
        "date"      : latest_date
    }


# ── MACD ──────────────────────────────────────────────────
def get_macd(ticker: str) -> dict:
    """
    Fetch MACD indicator.
    MACD > Signal line = Bullish crossover
    MACD < Signal line = Bearish crossover
    """
    data = fetch_av({
        "function"   : "MACD",
        "symbol"     : ticker,
        "interval"   : "daily",
        "series_type": "close"
    })

    if "Technical Analysis: MACD" not in data:
        return {"error": "MACD data unavailable"}

    macd_data   = data["Technical Analysis: MACD"]
    latest_date = sorted(macd_data.keys())[-1]
    latest      = macd_data[latest_date]

    macd_val    = float(latest["MACD"])
    signal_val  = float(latest["MACD_Signal"])
    hist_val    = float(latest["MACD_Hist"])

    crossover = "Bullish" if macd_val > signal_val else "Bearish"

    return {
        "ticker"    : ticker,
        "macd"      : round(macd_val, 4),
        "signal"    : round(signal_val, 4),
        "histogram" : round(hist_val, 4),
        "crossover" : crossover,
        "date"      : latest_date
    }


# ── Company Overview ──────────────────────────────────────
def get_company_overview(ticker: str) -> dict:
    """
    Fetch company fundamentals.
    Name, sector, market cap, P/E ratio, 52-week high/low.
    """
    data = fetch_av({
        "function": "OVERVIEW",
        "symbol"  : ticker
    })

    if "Symbol" not in data:
        return {"error": "Company data unavailable"}

    return {
        "ticker"      : ticker,
        "name"        : data.get("Name", ticker),
        "sector"      : data.get("Sector", "N/A"),
        "industry"    : data.get("Industry", "N/A"),
        "market_cap"  : data.get("MarketCapitalization", "N/A"),
        "pe_ratio"    : data.get("PERatio", "N/A"),
        "week_high_52": data.get("52WeekHigh", "N/A"),
        "week_low_52" : data.get("52WeekLow", "N/A"),
        "description" : data.get("Description", "")[:200]
    }


# ── Combined Insight ──────────────────────────────────────
def get_stock_insight(ticker: str) -> dict:
    """
    Combine RSI + MACD into one unified insight.
    Falls back gracefully if MACD unavailable.
    """
    rsi  = get_rsi(ticker)
    macd = get_macd(ticker)

    signals = []

    if "signal" in rsi and "error" not in rsi:
        signals.append(rsi["signal"])

    # Only use MACD if it actually returned data
    if "crossover" in macd and "error" not in macd:
        signals.append(macd["crossover"])

    # If no signals at all
    if not signals:
        return {
            "ticker" : ticker,
            "overall": "Neutral ➡️",
            "summary": "Insufficient data for full analysis",
            "rsi"    : rsi,
            "macd"   : macd
        }

    bullish_count = signals.count("Bullish")
    bearish_count = signals.count("Bearish")

    if bullish_count > bearish_count:
        overall = "Bullish 📈"
        summary = "Indicators suggest upward momentum"
    elif bearish_count > bullish_count:
        overall = "Bearish 📉"
        summary = "Indicators suggest downward pressure"
    else:
        overall = "Neutral ➡️"
        summary = "Mixed signals — market is undecided"

    return {
        "ticker" : ticker,
        "overall": overall,
        "summary": summary,
        "rsi"    : rsi,
        "macd"   : macd
    }

# ── Cached versions (saves API calls) ────────────────────
from sqlmodel import Session, select
from src.auth.models import APICache
import json


def get_cached_or_fetch(ticker: str, data_type: str,
                         fetch_fn, db: Session) -> dict:
    """
    Check database cache first.
    If data is less than 24 hours old → return cached.
    Otherwise → fetch fresh from Alpha Vantage.
    """
    # Check cache
    cached = db.exec(
        select(APICache)
        .where(
            APICache.ticker    == ticker,
            APICache.data_type == data_type
        )
    ).first()

    if cached:
        # Check if cache is still fresh (under 24 hours)
        age = datetime.utcnow() - cached.fetched_at.replace(tzinfo=None)
        if age < timedelta(hours=24):
            return json.loads(cached.data)

    # Cache miss or stale — fetch fresh data
    fresh_data = fetch_fn(ticker)

    # Save to cache
    if cached:
        cached.data       = json.dumps(fresh_data)
        cached.fetched_at = datetime.utcnow()
    else:
        cached = APICache(
            ticker    = ticker,
            data_type = data_type,
            data      = json.dumps(fresh_data)
        )
    db.add(cached)
    db.commit()

    return fresh_data