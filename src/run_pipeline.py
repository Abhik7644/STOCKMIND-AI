from src.data_loader   import fetch_stock_data
from src.preprocessor  import preprocess_pipeline
from src.train         import train_model
from src.predict       import predict
from src.evaluate      import get_metrics, plot_predictions
import numpy as np
import joblib

# Config
TICKER     = 'AAPL'
START      = '2019-01-01'
END        = '2024-01-01'
DATA_PATH  = 'data/AAPL_raw.csv'
MODEL_PATH = 'models/best_model.keras'
SCALER_PATH= 'models/scaler.pkl'
DATA_DIR   = 'data'

# Run
df = fetch_stock_data(TICKER, START, END, save_path=DATA_PATH)

X_train, X_test, y_train, y_test, scaler = preprocess_pipeline(
    df,
    scaler_path=SCALER_PATH,
    save_dir=DATA_DIR
)

model, history = train_model(X_train, y_train, model_path=MODEL_PATH)

predictions = predict(X_test, MODEL_PATH, SCALER_PATH)
actual      = scaler.inverse_transform(y_test.reshape(-1, 1))

get_metrics(actual, predictions)
plot_predictions(actual, predictions, ticker=TICKER)