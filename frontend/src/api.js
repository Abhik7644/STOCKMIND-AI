import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({ baseURL: BASE_URL });

// Auto-attach token to every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// ── Predictions ───────────────────────────────────────────
export const getPrediction  = (ticker) => api.get(`/api/predict?ticker=${ticker}`);
export const getHistory     = (ticker, days = 90) => api.get(`/api/history?ticker=${ticker}&days=${days}`);
export const getComparison  = (tickers) => api.get(`/api/compare?tickers=${tickers.join(',')}`);
export const getTopMovers   = () => api.get('/api/top-movers');

// ── Alpha Vantage ─────────────────────────────────────────
export const getInsights    = (ticker) => api.get(`/api/insights/${ticker}`);
export const getOverview    = (ticker) => api.get(`/api/overview/${ticker}`);

// ── Auth ──────────────────────────────────────────────────
export const loginUser      = (email, password) =>
  api.post('/api/auth/login', { email, password });

export const registerUser   = (email, username, password) =>
  api.post('/api/auth/register', { email, username, password });

export const getProfile     = () => api.get('/api/auth/me');

// ── Watchlist ─────────────────────────────────────────────
export const getWatchlist   = () => api.get('/api/auth/watchlist');
export const addWatchlist   = (ticker) =>
  api.post('/api/auth/watchlist', { ticker });
export const removeWatchlist = (ticker) =>
  api.delete(`/api/auth/watchlist/${ticker}`);

// ── Trades ────────────────────────────────────────────────
export const getTrades      = () => api.get('/api/auth/trades');
export const executeTrade   = (ticker, action, shares) =>
  api.post('/api/auth/trade', { ticker, action, shares });

// ── History ───────────────────────────────────────────────
export const getSearchHistory = () => api.get('/api/auth/history');

export default api;
