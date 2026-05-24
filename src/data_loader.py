import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker: str, start: str, end: str, save_path: str = None):
    """
    Fetch historical stock data from Yahoo Finance.
    
    Args:
        ticker    : stock symbol e.g. 'AAPL'
        start     : start date  e.g. '2019-01-01'
        end       : end date    e.g. '2024-01-01'
        save_path : optional CSV save path
    
    Returns:
        DataFrame with OHLCV columns
    """
    print(f"Fetching {ticker} data from {start} to {end}...")
    
    df = yf.download(ticker, start=start, end=end)

    # Fix multi-header issue
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path)
        print(f"Data saved to {save_path} ✅")

    print(f"Fetched {len(df)} trading days")
    return df


def load_stock_data(csv_path: str):
    """Load previously saved stock CSV."""
    df = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
    print(f"Loaded data: {len(df)} rows")
    return df