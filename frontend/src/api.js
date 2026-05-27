import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000';

export const getHealth = () =>
    axios.get(`${BASE_URL}/api/health`);

export const getPrediction = (ticker) =>
    axios.get(`${BASE_URL}/api/predict?ticker=${ticker}`);

export const getHistory = (ticker, days = 90) =>
    axios.get(`${BASE_URL}/api/history?ticker=${ticker}&days=${days}`);

export const getComparison = (tickers) =>
    axios.get(`${BASE_URL}/api/compare?tickers=${tickers.join(',')}`);

import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export const getHealth      = () =>
    axios.get(`${BASE_URL}/api/health`);

export const getPrediction  = (ticker) =>
    axios.get(`${BASE_URL}/api/predict?ticker=${ticker}`);

export const getHistory     = (ticker, days = 90) =>
    axios.get(`${BASE_URL}/api/history?ticker=${ticker}&days=${days}`);

export const getComparison  = (tickers) =>
    axios.get(`${BASE_URL}/api/compare?tickers=${tickers.join(',')}`);

// ── New Alpha Vantage endpoints ──────────────────────────
export const getInsights    = (ticker) =>
    axios.get(`${BASE_URL}/api/insights/${ticker}`);

export const getOverview    = (ticker) =>
    axios.get(`${BASE_URL}/api/overview/${ticker}`);

export const getTopMovers   = () =>
    axios.get(`${BASE_URL}/api/top-movers`);