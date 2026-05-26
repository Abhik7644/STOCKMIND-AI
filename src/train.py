from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from src.model import build_lstm
import os


def train_model(X_train, y_train, ticker: str,
                models_dir: str = 'models',
                epochs: int = 50, batch_size: int = 32):
    """
    Train LSTM model for a specific ticker.
    Saves model as {ticker}_model.keras

    Args:
        X_train    : training sequences
        y_train    : training targets
        ticker     : stock symbol e.g. 'AAPL'
        models_dir : directory to save model
        epochs     : max training epochs
        batch_size : samples per gradient update

    Returns:
        model, history
    """
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, f"{ticker}_model.keras")

    model = build_lstm(input_shape=(X_train.shape[1], 1))

    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1
    )

    print(f"Model saved → {model_path} ✅")
    return model, history