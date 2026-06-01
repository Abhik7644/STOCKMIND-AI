# 📈 StockMind AI

> **AI-powered stock price prediction web application** built with LSTM deep learning, FastAPI, and React. Predicts next-day closing prices for major US stocks using 5 years of historical market data.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=flat-square&logo=tensorflow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![SQLite](https://img.shields.io/badge/SQLite-SQLModel-lightgrey?style=flat-square&logo=sqlite)

---

## 🔗 Live Demo

|              | Link                                        |
| ------------ | ------------------------------------------- |
| **Frontend** | `https://stockmind-ai.vercel.app`           |
| **API Docs** | `https://stockmind-api.onrender.com/docs`   |
| **GitHub**   | `https://github.com/Abhik7644/STOCKMIND-AI` |

---

## 🧠 What It Does

StockMind AI fetches real market data, runs it through a trained LSTM neural network, and returns next-day price predictions along with RSI-based market signals and company fundamentals — all served through a REST API and displayed on a clean dark-themed dashboard.

```
User searches "AAPL"
        ↓
Backend loads AAPL's dedicated LSTM model
        ↓
Fetches last 60 days of real price data (yfinance)
        ↓
Normalizes → feeds into LSTM → inverse transforms
        ↓
Returns predicted price + RSI signal + company overview
        ↓
React dashboard displays chart + prediction card
```

---

## ✨ Features

### 🤖 AI Prediction Engine

- **Dedicated LSTM model per stock** — each stock has its own model trained purely on its own price history, not a generic shared model
- **2-layer LSTM architecture** with Dropout regularization to prevent overfitting
- **60-day sliding window** — model learns from the last 60 trading days to predict day 61
- **Per-stock MinMaxScaler** — each stock's price range is normalized independently, ensuring accuracy across stocks trading at wildly different prices
- **On-demand training** — if a user searches an unknown ticker (e.g. CSCO), the system automatically fetches 5 years of data, trains a new LSTM, saves it, and returns a prediction — all in the background
- **Prediction accuracy: MAPE 2.85%** on the AAPL test set

### 📊 Market Data & Insights

- **Real-time price data** via `yfinance` for model input
- **Alpha Vantage API integration** for:
  - RSI (Relative Strength Index) — 14-period
  - MACD indicator with bullish/bearish crossover detection
  - Company overview — sector, market cap, P/E ratio, 52-week high/low
  - Company description
- **Unified market signal** — combines RSI and MACD into one Overall signal: Bullish / Bearish / Neutral
- **User-friendly insight language** — no financial jargon, plain English explanations
- **24-hour API response caching** in SQLite — respects Alpha Vantage's 25 requests/day free limit

### 🏆 Pre-Trained Stock Models

10 major US stocks come with pre-trained models for instant predictions:

| Ticker | Company                | Sector           |
| ------ | ---------------------- | ---------------- |
| AAPL   | Apple Inc.             | Technology       |
| MSFT   | Microsoft              | Technology       |
| GOOGL  | Alphabet (Google)      | Technology       |
| TSLA   | Tesla                  | Automotive/EV    |
| AMZN   | Amazon                 | E-Commerce/Cloud |
| NVDA   | NVIDIA                 | Semiconductors   |
| META   | Meta Platforms         | Social Media     |
| NFLX   | Netflix                | Streaming        |
| AMD    | Advanced Micro Devices | Semiconductors   |
| JPM    | JPMorgan Chase         | Finance          |

Any other ticker triggers automatic on-demand training and gets added to the model library permanently.

### 📈 Interactive Dashboard

- **90-day price history chart** (Area chart with gradient fill)
- **Prediction dot** — gold dot showing tomorrow's predicted price on the chart
- **Top Gainers / Top Losers** — live predictions ranked across all 10 pre-trained stocks
- **Prediction card** — shows current price vs predicted price with % change and green/red coloring
- **RSI gauge** — visual slider showing RSI value with Oversold / Neutral / Overbought zones
- **Company overview panel** — sector, P/E ratio, 52-week high/low, company description
- **Ticker buttons** — one-click prediction for any pre-trained stock

### 🔐 Authentication System

- **JWT-based auth** — secure JSON Web Tokens for session management
- **Register / Login** — email + username + password
- **Protected routes** — watchlist and portfolio require login
- **bcrypt password hashing** — passwords never stored in plain text
- **Persistent sessions** — token stored in localStorage, auto-loaded on return

### ⭐ Watchlist

- Add any stock to personal watchlist with one click
- Watchlist visible on dashboard for quick access
- Per-user storage in SQLite database
- Click any watchlist item to instantly load that stock's prediction

### 💼 Paper Trading (Virtual Money)

- Every user starts with **$10,000 virtual balance**
- Execute BUY and SELL orders at real current market prices
- Balance updates in real-time after each trade
- Full trade history with ticker, action, shares, price, total value, and date
- No real money involved — purely for learning and simulation
- Great for testing trading strategies against AI predictions

### 🗄️ Database & Caching

- **SQLite via SQLModel** — zero setup, file-based, works everywhere
- **6 database tables**: users, search_history, watchlist, paper_trades, model_cache, api_cache
- **Alpha Vantage cache** — each API response stored for 24 hours, dramatically reducing daily API calls
- Easily swappable to PostgreSQL by changing one line in `.env`

---

## 🛠️ Tech Stack

### Backend

| Technology             | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| **Python 3.11**        | Core language                                     |
| **TensorFlow / Keras** | LSTM model building and training                  |
| **FastAPI**            | REST API framework                                |
| **SQLModel**           | Database ORM (SQLAlchemy + Pydantic combined)     |
| **SQLite**             | Database (file-based, zero setup)                 |
| **yfinance**           | Historical stock data for training and prediction |
| **Alpha Vantage API**  | RSI, MACD, company overview, news                 |
| **passlib + bcrypt**   | Password hashing                                  |
| **python-jose**        | JWT token creation and verification               |
| **scikit-learn**       | MinMaxScaler for data normalization               |
| **uvicorn**            | ASGI server                                       |

### Frontend

| Technology          | Purpose                   |
| ------------------- | ------------------------- |
| **React 18**        | UI framework              |
| **React Router v6** | Client-side routing       |
| **Recharts**        | Stock price area charts   |
| **Axios**           | HTTP client for API calls |
| **Lucide React**    | Icon library              |
| **CSS Modules**     | Scoped component styling  |

---

## 📁 Project Structure

```
Stock-Predictor/
├── src/                          # Python backend
│   ├── app.py                    # FastAPI app + all endpoints
│   ├── database.py               # SQLite connection + session
│   ├── alpha_vantage.py          # Alpha Vantage service
│   ├── data_loader.py            # yfinance data fetching
│   ├── preprocessor.py           # Normalization + sliding windows
│   ├── model.py                  # LSTM architecture definition
│   ├── train.py                  # Single stock training
│   ├── train_all.py              # Batch train all 10 stocks
│   ├── predict.py                # Load model + predict
│   ├── evaluate.py               # MAE, RMSE, MAPE metrics
│   ├── run_pipeline.py           # End-to-end pipeline script
│   └── auth/
│       ├── models.py             # SQLModel database tables
│       ├── schemas.py            # Request/response schemas
│       ├── security.py           # JWT + bcrypt
│       ├── crud.py               # Database operations
│       └── router.py             # Auth API endpoints
│
├── models/                       # Saved trained models (gitignored)
│   ├── AAPL_model.keras
│   ├── AAPL_scaler.pkl
│   └── ... (one pair per stock)
│
├── data/                         # Training data (gitignored)
│   ├── AAPL_raw.csv
│   └── ...
│
├── notebooks/                    # Jupyter exploration notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_evaluation.ipynb
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── App.js
│   │   ├── api.js                # All API call functions
│   │   ├── globals.css
│   │   ├── context/
│   │   │   ├── AuthContext.js    # Login state management
│   │   │   └── StockContext.js   # Stock data state
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   └── MainLayout.jsx
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx
│   │       ├── AIPredictions.jsx
│   │       ├── Portfolio.jsx
│   │       └── Settings.jsx
│   └── package.json
│
├── .env                          # Environment variables (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1 — Clone the Repository

```bash
git clone https://github.com/Abhik7644/STOCKMIND-AI.git
cd STOCKMIND-AI
```

### 2 — Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3 — Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./stockmind.db
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALPHA_VANTAGE_KEY=your-alpha-vantage-key-here
```

Get a free Alpha Vantage key at: https://www.alphavantage.co/support/#api-key

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4 — Train the Models

```bash
# Pre-train all 10 stock models (~20 minutes)
python -m src.train_all
```

This creates `models/AAPL_model.keras`, `models/AAPL_scaler.pkl`, etc. for all 10 stocks.

### 5 — Start the Backend

```bash
uvicorn src.app:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

### 6 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create frontend environment file
echo "REACT_APP_API_URL=http://127.0.0.1:8000" > .env

# Start development server
npm start
```

App opens at `http://localhost:3000`

---

## 🔌 API Endpoints

### Predictions

| Method | Endpoint                              | Description                       |
| ------ | ------------------------------------- | --------------------------------- |
| GET    | `/api/health`                         | API health check                  |
| GET    | `/api/predict?ticker=AAPL`            | Next-day price prediction         |
| GET    | `/api/history?ticker=AAPL&days=90`    | 90-day price history + prediction |
| GET    | `/api/compare?tickers=AAPL,MSFT,TSLA` | Compare multiple stocks           |
| GET    | `/api/top-movers`                     | Top gainers and losers            |

### Insights (Alpha Vantage)

| Method | Endpoint                 | Description          |
| ------ | ------------------------ | -------------------- |
| GET    | `/api/insights/{ticker}` | RSI + MACD signals   |
| GET    | `/api/overview/{ticker}` | Company fundamentals |

### Authentication

| Method | Endpoint                       | Description                 |
| ------ | ------------------------------ | --------------------------- |
| POST   | `/api/auth/register`           | Create new account          |
| POST   | `/api/auth/login`              | Login, returns JWT          |
| GET    | `/api/auth/me`                 | Get current user profile    |
| GET    | `/api/auth/history`            | Search history              |
| POST   | `/api/auth/watchlist`          | Add to watchlist            |
| GET    | `/api/auth/watchlist`          | Get watchlist               |
| DELETE | `/api/auth/watchlist/{ticker}` | Remove from watchlist       |
| POST   | `/api/auth/trade`              | Execute paper trade         |
| GET    | `/api/auth/trades`             | Get trade history + balance |

---

## 🧪 Model Performance

| Metric   | Score     | Meaning                             |
| -------- | --------- | ----------------------------------- |
| **MAE**  | $4.99     | Average dollar error per prediction |
| **RMSE** | $5.74     | Root mean squared error             |
| **MAPE** | **2.85%** | Mean absolute percentage error      |

Evaluated on AAPL test set (20% holdout, ~240 trading days).

### Model Architecture

```
Input: (60, 1) — 60 days of normalized closing prices

Layer 1: LSTM(64, return_sequences=True)  → 16,896 params
Layer 2: Dropout(0.2)
Layer 3: LSTM(64, return_sequences=False) → 33,024 params
Layer 4: Dropout(0.2)
Layer 5: Dense(1)                         → 65 params

Total: 49,985 trainable parameters
Optimizer: Adam | Loss: Mean Squared Error
```

### Training Config

- **Training data**: 2020–2025 (5 years, ~1,260 trading days)
- **Train/test split**: 80% / 20% (time-based, never shuffled)
- **Epochs**: Up to 50 with EarlyStopping (patience=10)
- **Batch size**: 32
- **Best model**: Saved automatically via ModelCheckpoint

---

## 📱 Screenshots

> Dashboard — Prediction card, RSI insight, company overview, top movers

> AI Predictions — Full market scan across all 10 stocks

> Portfolio — Paper trading with trade history and balance

> Login — Register / login with animated grid background

---

## ⚙️ How It Works — Deep Dive

### Data Pipeline

```
yfinance.download("AAPL", start="2020-01-01")
        ↓
MinMaxScaler.fit_transform(close_prices)  # normalize to 0-1
        ↓
create_sequences(data, window=60)          # sliding window
        ↓
X shape: (samples, 60, 1)                 # LSTM input format
y shape: (samples,)                        # next day price
        ↓
80/20 time-based split                     # no shuffling
```

### Prediction Flow

```
User requests prediction for AAPL
        ↓
ensure_model_exists("AAPL")  →  loads AAPL_model.keras
        ↓
yfinance fetches last 6 months of AAPL data
        ↓
AAPL_scaler.transform(last_60_days)        # normalize
        ↓
model.predict(sequence)                    # LSTM inference
        ↓
AAPL_scaler.inverse_transform(prediction)  # back to dollars
        ↓
Return { current: $312, predicted: $318, change: +1.9% }
```

### On-Demand Training

```
User searches "CSCO" (not pre-trained)
        ↓
model_exists("CSCO") → False
        ↓
fetch_stock_data("CSCO", "2020-01-01", today)
        ↓
preprocess_pipeline(df, ticker="CSCO")
        ↓
train_model(X_train, y_train, ticker="CSCO")
        ↓
Save CSCO_model.keras + CSCO_scaler.pkl
        ↓
Next CSCO request → instant prediction
```

---

## 🌐 Deployment

### Backend → Render

1. Add `render.yaml` to project root:

```yaml
services:
  - type: web
    name: stockmind-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.app:app --host 0.0.0.0 --port $PORT
```

2. Push models to GitHub (remove `models/` from `.gitignore`)
3. Connect repo to [render.com](https://render.com)
4. Add environment variables in Render dashboard

### Frontend → Vercel

1. Create `frontend/.env.production`:

```
REACT_APP_API_URL=https://your-render-url.onrender.com
```

2. Connect `frontend/` folder to [vercel.com](https://vercel.com)
3. Set root directory to `frontend`
4. Deploy

---

## 📋 Known Limitations

- Predictions are based on **price history only** — does not account for news events, earnings, or macroeconomic changes
- Free Alpha Vantage tier has **25 API calls/day** — caching mitigates this but limits real-time freshness
- LSTM models require **periodic retraining** as markets evolve (recommended every 3-6 months)
- **Paper trading** uses virtual money only — not connected to any real brokerage
- On-demand training for unknown tickers takes **2-3 minutes** — shows loading state in UI

---

## 🔮 Future Improvements

- [ ] Multi-feature LSTM (9 inputs: OHLCV + RSI + MACD + VIX + Interest Rate)
- [ ] News sentiment feed with bullish/bearish tagging
- [ ] BUY / WAIT / HIGH RISK recommendation engine with confidence score
- [ ] WebSocket real-time price updates
- [ ] Scheduled model retraining pipeline (weekly)
- [ ] Expand to 30+ stocks across sectors
- [ ] Mobile-responsive design improvements
- [ ] Email notifications for watchlist price alerts

---

> ⚠️ **Disclaimer**: StockMind AI is a learning project and does not constitute financial advice. Never make real investment decisions based solely on AI predictions. Past performance does not guarantee future results.
