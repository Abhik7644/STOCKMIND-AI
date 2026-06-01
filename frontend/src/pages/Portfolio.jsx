import { useState, useEffect } from 'react';
import { useAuth }             from '../context/AuthContext';
import { getTrades, executeTrade, getPrediction } from '../api';
import Header from '../components/Header';
import styles from './Portfolio.module.css';
import { TrendingUp, TrendingDown, Plus } from 'lucide-react';

export default function Portfolio() {
  const { user, token } = useAuth();
  const [trades,   setTrades]   = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [ticker,   setTicker]   = useState('AAPL');
  const [action,   setAction]   = useState('BUY');
  const [shares,   setShares]   = useState(1);
  const [price,    setPrice]    = useState(null);
  const [message,  setMessage]  = useState('');
  const [error,    setError]    = useState('');

  useEffect(() => {
    if (token) loadTrades();
  }, [token]);

  const loadTrades = async () => {
    try {
      const res = await getTrades();
      setTrades(res.data.trades || []);
    } catch (_) {}
  };

  const fetchPrice = async () => {
    try {
      const res = await getPrediction(ticker.toUpperCase());
      setPrice(res.data.current_price);
    } catch (_) { setPrice(null); }
  };

  const handleTrade = async (e) => {
    e.preventDefault();
    setError(''); setMessage('');
    setLoading(true);
    try {
      const res = await executeTrade(ticker.toUpperCase(), action, parseFloat(shares));
      setMessage(`${action} executed! New balance: $${res.data.new_balance?.toFixed(2)}`);
      loadTrades();
    } catch (err) {
      setError(err.response?.data?.detail || 'Trade failed.');
    }
    setLoading(false);
  };

  if (!token) return (
    <div className={styles.page}>
      <Header title="Portfolio" />
      <div className={styles.locked}>
        <p>Please login to access paper trading.</p>
      </div>
    </div>
  );

  return (
    <div className={styles.page}>
      <Header title="Portfolio" />
      <div className={styles.body}>

        {/* Balance Card */}
        <div className={styles.balanceCard}>
          <p className={styles.balanceLabel}>Paper Trading Balance</p>
          <p className={styles.balanceValue}>
            ${user?.paper_balance?.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </p>
          <p className={styles.balanceSub}>Virtual money — no real investment</p>
        </div>

        {/* Trade Form */}
        <div className={styles.tradeCard}>
          <h3 className={styles.tradeTitle}>
            <Plus size={16} /> Execute Paper Trade
          </h3>

          <form onSubmit={handleTrade} className={styles.tradeForm}>
            <div className={styles.tradeRow}>
              <div className={styles.field}>
                <label>Ticker</label>
                <input
                  value={ticker}
                  onChange={e => setTicker(e.target.value.toUpperCase())}
                  onBlur={fetchPrice}
                  placeholder="AAPL"
                  maxLength={5}
                />
              </div>
              <div className={styles.field}>
                <label>Action</label>
                <select value={action} onChange={e => setAction(e.target.value)}>
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
              <div className={styles.field}>
                <label>Shares</label>
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={shares}
                  onChange={e => setShares(e.target.value)}
                />
              </div>
              <div className={styles.field}>
                <label>Est. Total</label>
                <div className={styles.estTotal}>
                  {price ? `$${(price * shares).toFixed(2)}` : '—'}
                </div>
              </div>
            </div>

            {message && <p className={styles.success}>{message}</p>}
            {error   && <p className={styles.error}>{error}</p>}

            <button
              type="submit"
              className={`${styles.tradeBtn} ${action === 'BUY' ? styles.buyBtn : styles.sellBtn}`}
              disabled={loading}
            >
              {loading ? 'Processing…' : `${action} ${shares} share(s) of ${ticker}`}
            </button>
          </form>
        </div>

        {/* Trade History */}
        <div className={styles.histCard}>
          <h3 className={styles.histTitle}>Trade History</h3>
          {trades.length === 0 ? (
            <p className={styles.empty}>No trades yet. Execute your first paper trade above.</p>
          ) : (
            <div className={styles.table}>
              <div className={styles.tableHead}>
                <span>Ticker</span>
                <span>Action</span>
                <span>Shares</span>
                <span>Price</span>
                <span>Total</span>
                <span>Date</span>
              </div>
              {trades.map((t, i) => (
                <div key={i} className={styles.tableRow}>
                  <span className={styles.rowTicker}>{t.ticker}</span>
                  <span className={t.action === 'BUY' ? styles.green : styles.red}>
                    {t.action === 'BUY' ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                    {' '}{t.action}
                  </span>
                  <span>{t.shares}</span>
                  <span>${t.price_at_trade?.toFixed(2)}</span>
                  <span>${t.total_value?.toFixed(2)}</span>
                  <span className={styles.rowDate}>
                    {t.traded_at ? new Date(t.traded_at).toLocaleDateString() : '—'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
