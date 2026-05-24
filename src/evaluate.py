import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error


def get_metrics(actual, predictions):
    """Calculate and print MAE, RMSE, MAPE."""
    mae  = mean_absolute_error(actual, predictions)
    rmse = np.sqrt(mean_squared_error(actual, predictions))
    mape = np.mean(np.abs((actual - predictions) / actual)) * 100

    metrics = {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}

    print(f"MAE:  ${mae:.2f}")
    print(f"RMSE: ${rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")

    return metrics


def plot_predictions(actual, predictions, ticker='AAPL'):
    """Plot actual vs predicted prices."""
    plt.figure(figsize=(14, 5))
    plt.plot(actual,      label='Actual Price',    color='royalblue', linewidth=1.5)
    plt.plot(predictions, label='Predicted Price', color='tomato',
             linewidth=1.5, linestyle='--')
    plt.title(f'{ticker} — Actual vs Predicted Close Price')
    plt.xlabel('Trading Days (Test Set)')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()