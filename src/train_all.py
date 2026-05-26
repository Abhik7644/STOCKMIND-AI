"""
Pre-train models for top 10 stocks.
Run once: python -m src.train_all
Takes ~15-20 minutes total.
"""
from src.data_loader  import fetch_stock_data
from src.preprocessor import preprocess_pipeline
from src.train        import train_model
import os

# Top 10 stocks to pre-train
TICKERS = [
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'GOOGL', # Google
    'TSLA',  # Tesla
    'AMZN',  # Amazon
    'NVDA',  # Nvidia
    'META',  # Meta
    'NFLX',  # Netflix
    'AMD',   # AMD
    'JPM',   # JPMorgan
]

MODELS_DIR = 'models'
DATA_DIR   = 'data'
START      = '2019-01-01'
END        = '2024-01-01'


def train_ticker(ticker: str):
    print(f"\n{'='*50}")
    print(f"  Training {ticker}")
    print(f"{'='*50}")

    try:
        # Fetch data
        df = fetch_stock_data(
            ticker, START, END,
            save_path=os.path.join(DATA_DIR, f"{ticker}_raw.csv")
        )

        # Preprocess
        X_train, X_test, y_train, y_test, scaler = preprocess_pipeline(
            df,
            ticker=ticker,
            models_dir=MODELS_DIR,
            save_dir=DATA_DIR
        )

        # Train
        model, history = train_model(
            X_train, y_train,
            ticker=ticker,
            models_dir=MODELS_DIR
        )

        print(f"✅ {ticker} done!")
        return True

    except Exception as e:
        print(f"❌ {ticker} failed: {e}")
        return False


if __name__ == '__main__':
    # Skip AAPL if already trained
    results = {}
    for ticker in TICKERS:
        if ticker == 'AAPL':
            print(f"\nSkipping AAPL — already trained ✅")
            results[ticker] = True
            continue
        results[ticker] = train_ticker(ticker)

    # Summary
    print(f"\n{'='*50}")
    print("  TRAINING SUMMARY")
    print(f"{'='*50}")
    for ticker, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {ticker}")