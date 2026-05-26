import numpy as np
import joblib
import os
from tensorflow.keras.models import load_model


def load_model_and_scaler(ticker: str, models_dir: str = 'models'):
    """Load ticker-specific model and scaler."""
    model_path  = os.path.join(models_dir, f"{ticker}_model.keras")
    scaler_path = os.path.join(models_dir, f"{ticker}_scaler.pkl")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for {ticker}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"No scaler found for {ticker}")

    model  = load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler


def model_exists(ticker: str, models_dir: str = 'models') -> bool:
    """Check if a trained model exists for this ticker."""
    model_path  = os.path.join(models_dir, f"{ticker}_model.keras")
    scaler_path = os.path.join(models_dir, f"{ticker}_scaler.pkl")
    return os.path.exists(model_path) and os.path.exists(scaler_path)


def predict(X_test, ticker: str, models_dir: str = 'models'):
    """Make predictions using ticker-specific model."""
    model, scaler = load_model_and_scaler(ticker, models_dir)
    predictions_scaled = model.predict(X_test, verbose=0)
    predictions = scaler.inverse_transform(predictions_scaled)
    return predictions