import numpy as np
import joblib
from tensorflow.keras.models import load_model


def predict(X_test, model_path: str, scaler_path: str):
    """
    Load saved model and make predictions.
    
    Returns:
        predictions : real dollar values
        actual      : real dollar values
    """
    model  = load_model(model_path)
    scaler = joblib.load(scaler_path)

    predictions_scaled = model.predict(X_test)

    predictions = scaler.inverse_transform(predictions_scaled)
    return predictions