import numpy as np
import joblib
import os
from sklearn.preprocessing import MinMaxScaler


def normalize(data, scaler_path: str = None):
    """
    Normalize data to 0-1 range.
    Saves scaler if path is provided.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(data)

    if scaler_path:
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
        joblib.dump(scaler, scaler_path)
        print(f"Scaler saved to {scaler_path} ✅")

    return scaled, scaler


def create_sequences(data, window_size: int = 60):
    """
    Create sliding window sequences for LSTM.
    
    Args:
        data        : normalized 1D array
        window_size : number of past days to look at
    
    Returns:
        X shape: (samples, window_size, 1)
        y shape: (samples,)
    """
    X, y = [], []
    for i in range(window_size, len(data)):
        X.append(data[i - window_size:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


def split_data(X, y, split_ratio: float = 0.80):
    """Time-based train/test split — never shuffle."""
    split = int(len(X) * split_ratio)
    return X[:split], X[split:], y[:split], y[split:]


def reshape_for_lstm(X):
    """Reshape to (samples, timesteps, 1) for LSTM input."""
    return X.reshape((X.shape[0], X.shape[1], 1))


def preprocess_pipeline(df, ticker: str, window_size=60,
                         split_ratio=0.80, models_dir='models',
                         save_dir=None):
    """
    Full preprocessing pipeline for a specific ticker.
    Saves scaler as {ticker}_scaler.pkl
    """
    import os
    os.makedirs(models_dir, exist_ok=True)
    scaler_path = os.path.join(models_dir, f"{ticker}_scaler.pkl")

    data = df[['Close']].values

    scaled, scaler = normalize(data, scaler_path)
    X, y           = create_sequences(scaled, window_size)
    X_train, X_test, y_train, y_test = split_data(X, y, split_ratio)
    X_train = reshape_for_lstm(X_train)
    X_test  = reshape_for_lstm(X_test)

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        np.save(f"{save_dir}/{ticker}_X_train.npy", X_train)
        np.save(f"{save_dir}/{ticker}_X_test.npy",  X_test)
        np.save(f"{save_dir}/{ticker}_y_train.npy", y_train)
        np.save(f"{save_dir}/{ticker}_y_test.npy",  y_test)
        print(f"Arrays saved to {save_dir} ✅")

    print(f"X_train: {X_train.shape} | X_test: {X_test.shape}")
    return X_train, X_test, y_train, y_test, scaler