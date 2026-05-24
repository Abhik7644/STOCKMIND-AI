from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from src.model import build_lstm


def train_model(X_train, y_train, model_path: str, epochs=50, batch_size=32):
    """
    Train LSTM model with callbacks.
    
    Args:
        X_train    : training sequences
        y_train    : training targets
        model_path : where to save the best model
        epochs     : max training epochs
        batch_size : samples per gradient update
    
    Returns:
        model, history
    """
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

    print(f"Model saved to {model_path} ✅")
    return model, history