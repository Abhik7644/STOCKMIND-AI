import { createContext, useContext, useState, useCallback } from 'react';
import { getPrediction, getHistory, getInsights,
         getOverview, getTopMovers } from '../api';

const StockContext = createContext();

export function StockProvider({ children }) {
  const [activeTicker, setActiveTicker] = useState('AAPL');
  const [prediction,   setPrediction]   = useState(null);
  const [history,      setHistory]      = useState([]);
  const [insight,      setInsight]      = useState(null);
  const [overview,     setOverview]     = useState(null);
  const [topMovers,    setTopMovers]    = useState(null);
  const [loading,      setLoading]      = useState(false);
  const [error,        setError]        = useState(null);

  const fetchStock = useCallback(async (ticker) => {
    setLoading(true);
    setError(null);
    setActiveTicker(ticker);
    try {
      const [predRes, histRes, insightRes, overviewRes] = await Promise.all([
        getPrediction(ticker),
        getHistory(ticker, 90),
        getInsights(ticker),
        getOverview(ticker)
      ]);

      setPrediction(predRes.data);
      setInsight(insightRes.data);
      setOverview(overviewRes.data);

      // Format chart data
      const chartData = histRes.data.dates.map((date, i) => ({
        date,
        price: histRes.data.prices[i]
      }));
      const lastDate = new Date(histRes.data.dates.at(-1));
      lastDate.setDate(lastDate.getDate() + 1);
      chartData.push({
        date      : lastDate.toISOString().split('T')[0],
        price     : null,
        prediction: histRes.data.prediction
      });
      setHistory(chartData);

    } catch (err) {
      setError(`Could not load data for ${ticker}`);
    }
    setLoading(false);
  }, []);

  const fetchTopMovers = useCallback(async () => {
    try {
      const res = await getTopMovers();
      setTopMovers(res.data);
    } catch (_) {}
  }, []);

  return (
    <StockContext.Provider value={{
      activeTicker, prediction, history,
      insight, overview, topMovers,
      loading, error,
      fetchStock, fetchTopMovers
    }}>
      {children}
    </StockContext.Provider>
  );
}

export const useStock = () => useContext(StockContext);
