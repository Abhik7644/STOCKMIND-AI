from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


def build_lstm(input_shape, units=64, dropout=0.2):
    """
    Build and compile the LSTM model.
    
    Args:
        input_shape : (window_size, 1) e.g. (60, 1)
        units       : LSTM neurons per layer
        dropout     : dropout rate
    
    Returns:
        Compiled Keras model
    """
    model = Sequential([
        LSTM(units, return_sequences=True, input_shape=input_shape),
        Dropout(dropout),
        LSTM(units, return_sequences=False),
        Dropout(dropout),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')
    
    print(model.summary())
    return model