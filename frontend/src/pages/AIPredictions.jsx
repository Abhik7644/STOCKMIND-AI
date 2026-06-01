import { useState }     from 'react';
import { useStock }     from '../context/StockContext';
import { getPrediction } from '../api';
import Header            from '../components/Header';
import styles            from './Predictions.module.css';
import { Brain, Zap, RefreshCw } from 'lucide-react';

const TICKERS = ['AAPL','MSFT','GOOGL','TSLA','AMZN','NVDA','META','NFLX','AMD','JPM'];

export default function AIPredictions() {
  const { fetchStock, prediction, insight, loading } = useStock();
  const [results, setResults]   = useState([]);
  const [scanning, setScanning] = useState(false);

  const scanAll = async () => {
    setScanning(true);
    setResults([]);
    for (const t of TICKERS) {
      try {
        const res = await getPrediction(t);
        setResults(prev => [...prev, res.data]);
      } catch (_) {}
    }
    setScanning(false);
  };

  return (
    <div className={styles.page}>
      <Header title="AI Predictions" />
      <div className={styles.body}>

        <div className={styles.topRow}>
          <div className={styles.intro}>
            <Brain size={20} style={{ color: 'var(--purple)' }} />
            <div>
              <h2>LSTM Prediction Engine</h2>
              <p>Each stock has its own dedicated model trained on 5 years of historical data.</p>
            </div>
          </div>
          <button
            className={styles.scanBtn}
            onClick={scanAll}
            disabled={scanning}
          >
            {scanning
              ? <><RefreshCw size={14} className={styles.spin} /> Scanning…</>
              : <><Zap size={14} /> Scan All Stocks</>
            }
          </button>
        </div>

        {/* Quick predict buttons */}
        <div className={styles.tickerGrid}>
          {TICKERS.map(t => (
            <button
              key={t}
              className={styles.tickerBtn}
              onClick={() => fetchStock(t)}
              disabled={loading}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Current prediction */}
        {prediction && (
          <div className={styles.predResult}>
            <div className={styles.predResultHeader}>
              <h3>{prediction.ticker}</h3>
              <span className={
                prediction.change >= 0 ? styles.green : styles.red
              }>
                {prediction.change >= 0 ? '▲' : '▼'}
                {' '}{Math.abs(prediction.change_pct).toFixed(2)}%
              </span>
            </div>
            <div className={styles.predResultBody}>
              <div className={styles.predResultItem}>
                <span>Current Price</span>
                <strong>${prediction.current_price}</strong>
              </div>
              <div className={styles.predResultItem}>
                <span>Predicted Price</span>
                <strong>${prediction.predicted_price}</strong>
              </div>
              <div className={styles.predResultItem}>
                <span>Model Status</span>
                <strong>{prediction.model_status === 'pretrained' ? '⚡ Pre-trained' : '🔧 On-demand'}</strong>
              </div>
              {insight?.overall && (
                <div className={styles.predResultItem}>
                  <span>Signal</span>
                  <strong>{insight.overall}</strong>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Scan results */}
        {results.length > 0 && (
          <div className={styles.scanResults}>
            <h3 className={styles.scanTitle}>Full Market Scan</h3>
            <div className={styles.scanGrid}>
              {results
                .sort((a, b) => b.change_pct - a.change_pct)
                .map(r => (
                  <div
                    key={r.ticker}
                    className={`${styles.scanCard} ${r.change >= 0 ? styles.scanUp : styles.scanDown}`}
                    onClick={() => fetchStock(r.ticker)}
                  >
                    <p className={styles.scanTicker}>{r.ticker}</p>
                    <p className={styles.scanPrice}>${r.predicted_price}</p>
                    <p className={`${styles.scanPct} ${r.change >= 0 ? styles.green : styles.red}`}>
                      {r.change >= 0 ? '▲' : '▼'} {Math.abs(r.change_pct).toFixed(2)}%
                    </p>
                  </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
