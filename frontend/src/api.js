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