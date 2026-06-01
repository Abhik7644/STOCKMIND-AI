import { useEffect, useState } from 'react';
import { useStock }            from '../context/StockContext';
import { useAuth }             from '../context/AuthContext';
import { addWatchlist, getTrades } from '../api';
import {
  AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, Star, StarOff,
         RefreshCw, Building2, BarChart2 } from 'lucide-react';
import Header  from '../components/Header';
import styles  from './Dashboard.module.css';

// ── Subcomponents ─────────────────────────────────────────

function StatCard({ label, value, sub, color }) {
  return (
    <div className={styles.statCard} style={{ borderTopColor: color }}>
      <p className={styles.statLabel}>{label}</p>
      <p className={styles.statValue}>{value}</p>
      {sub && <p className={styles.statSub} style={{ color }}>{sub}</p>}
    </div>
  );
}

function MoverRow({ data, onSelect }) {
  const up = data.change_pct >= 0;
  return (
    <div className={styles.moverRow} onClick={() => onSelect(data.ticker)}>
      <span className={styles.moverTicker}>{data.ticker}</span>
      <span className={styles.moverPrice}>${data.current_price}</span>
      <span className={`${styles.moverPct} ${up ? styles.green : styles.red}`}>
        {up ? '▲' : '▼'} {Math.abs(data.change_pct).toFixed(2)}%
      </span>
    </div>
  );
}

function RSIGauge({ value }) {
  if (!value) return null;
  const pct   = (value / 100) * 100;
  const color = value < 30 ? 'var(--green)' : value > 70 ? 'var(--red)' : 'var(--yellow)';
  return (
    <div className={styles.rsiGauge}>
      <div className={styles.rsiBar}>
        <div className={styles.rsiZones}>
          <span style={{ color: 'var(--green)', fontSize: '0.65rem' }}>Oversold</span>
          <span style={{ color: 'var(--yellow)', fontSize: '0.65rem' }}>Neutral</span>
          <span style={{ color: 'var(--red)', fontSize: '0.65rem' }}>Overbought</span>
        </div>
        <div className={styles.rsiTrack}>
          <div
            className={styles.rsiFill}
            style={{ width: `${pct}%`, background: color }}
          />
          <div
            className={styles.rsiThumb}
            style={{ left: `calc(${pct}% - 6px)`, background: color }}
          />
        </div>
      </div>
      <p className={styles.rsiValue} style={{ color }}>
        RSI {value} — {value < 30 ? 'Oversold' : value > 70 ? 'Overbought' : 'Neutral'}
      </p>
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <p className={styles.ttDate}>{label}</p>
      <p className={styles.ttPrice}>${payload[0].value?.toFixed(2)}</p>
    </div>
  );
}

// ── Main Dashboard ────────────────────────────────────────
export default function Dashboard() {
  const {
    activeTicker, prediction, history,
    insight, overview, topMovers,
    loading, error,
    fetchStock, fetchTopMovers
  } = useStock();

  const { token, user } = useAuth();
  const [watchlisted, setWatchlisted] = useState(false);
  const [starLoading, setStarLoading] = useState(false);

  useEffect(() => {
    fetchStock('AAPL');
    fetchTopMovers();
  }, []);

  const handleWatchlist = async () => {
    if (!token) return;
    setStarLoading(true);
    try {
      await addWatchlist(activeTicker);
      setWatchlisted(true);
      setTimeout(() => setWatchlisted(false), 3000);
    } catch (_) {}
    setStarLoading(false);
  };

  const isUp = prediction && prediction.change >= 0;

  return (
    <div className={styles.page}>
      <Header title="Dashboard" />

      <div className={styles.body}>

        {/* ── Stats Row ── */}
        <div className={styles.statsRow}>
          <StatCard
            label="Prediction Accuracy"
            value="2.85%"
            sub="MAPE on test set"
            color="var(--accent)"
          />
          <StatCard
            label="Models Trained"
            value="10"
            sub="Pre-trained stocks"
            color="var(--purple)"
          />
          <StatCard
            label="Training Data"
            value="5 Years"
            sub="2019 – 2024"
            color="var(--cyan)"
          />
          <StatCard
            label="Paper Balance"
            value={user ? `$${user.paper_balance?.toLocaleString('en-US', { maximumFractionDigits: 0 })}` : '$10,000'}
            sub="Virtual trading"
            color="var(--green)"
          />
        </div>

        {/* ── Main Grid ── */}
        <div className={styles.grid}>

          {/* Left — Prediction + Chart */}
          <div className={styles.leftCol}>

            {/* Prediction Card */}
            {prediction && (
              <div className={`${styles.predCard} ${isUp ? styles.predUp : styles.predDown}`}>
                <div className={styles.predLeft}>
                  <p className={styles.predLabel}>Next Day Prediction</p>
                  <h2 className={styles.predTicker}>{prediction.ticker}</h2>
                  <p className={styles.predCurrent}>
                    Current Price
                    <strong> ${prediction.current_price}</strong>
                  </p>
                  {insight?.rsi && (
                    <span
                      className={styles.signalBadge}
                      style={{
                        color: insight.rsi.color === 'green'
                          ? 'var(--green)' : insight.rsi.color === 'red'
                          ? 'var(--red)' : 'var(--yellow)',
                        borderColor: insight.rsi.color === 'green'
                          ? 'var(--green)' : insight.rsi.color === 'red'
                          ? 'var(--red)' : 'var(--yellow)',
                      }}
                    >
                      {insight.overall}
                    </span>
                  )}
                </div>

                <div className={styles.predRight}>
                  {loading
                    ? <RefreshCw size={20} className={styles.spin} />
                    : <p className={styles.predPrice}>${prediction.predicted_price}</p>
                  }
                  <div className={`${styles.predChange} ${isUp ? styles.green : styles.red}`}>
                    {isUp ? <TrendingUp size={18}/> : <TrendingDown size={18}/>}
                    <span>
                      {isUp ? '+' : ''}{prediction.change} ({prediction.change_pct}%)
                    </span>
                  </div>
                  {token && (
                    <button
                      className={`${styles.starBtn} ${watchlisted ? styles.starred : ''}`}
                      onClick={handleWatchlist}
                      disabled={starLoading}
                    >
                      {watchlisted ? <StarOff size={14}/> : <Star size={14}/>}
                      {watchlisted ? 'Added!' : 'Watchlist'}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Error */}
            {error && <div className={styles.errorBanner}>{error}</div>}

            {/* Chart */}
            <div className={styles.chartCard}>
              <div className={styles.chartHeader}>
                <h3>90-Day Price History + Prediction</h3>
                {loading && <RefreshCw size={14} className={styles.spin} />}
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={history}
                  margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                    tickFormatter={d => d.slice(5)}
                    interval={14}
                  />
                  <YAxis
                    tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                    domain={['auto','auto']}
                    tickFormatter={v => `$${v}`}
                    width={55}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fill="url(#grad)"
                    connectNulls={false}
                    dot={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="prediction"
                    stroke="#f59e0b"
                    strokeWidth={0}
                    fill="#f59e0b"
                    dot={{ r: 7, fill: '#f59e0b', stroke: '#fff', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

          </div>

          {/* Right — Insights + Movers */}
          <div className={styles.rightCol}>

            {/* RSI Insight */}
            {insight && (
              <div className={styles.insightCard}>
                <div className={styles.insightHeader}>
                  <BarChart2 size={16} style={{ color: 'var(--purple)' }} />
                  <h3>Market Insight</h3>
                </div>
                <p className={styles.insightOverall}>{insight.overall}</p>
                <p className={styles.insightSummary}>{insight.summary}</p>
                {insight.rsi?.rsi && (
                  <RSIGauge value={insight.rsi.rsi} />
                )}
                {insight.rsi?.message && (
                  <p className={styles.insightMsg}>{insight.rsi.message}</p>
                )}
              </div>
            )}

            {/* Company Overview */}
            {overview && !overview.error && (
              <div className={styles.overviewCard}>
                <div className={styles.overviewHeader}>
                  <Building2 size={16} style={{ color: 'var(--cyan)' }} />
                  <h3>{overview.name}</h3>
                </div>
                <div className={styles.overviewGrid}>
                  <div className={styles.overviewItem}>
                    <span>Sector</span>
                    <strong>{overview.sector}</strong>
                  </div>
                  <div className={styles.overviewItem}>
                    <span>P/E Ratio</span>
                    <strong>{overview.pe_ratio}</strong>
                  </div>
                  <div className={styles.overviewItem}>
                    <span>52W High</span>
                    <strong style={{ color: 'var(--green)' }}>${overview.week_high_52}</strong>
                  </div>
                  <div className={styles.overviewItem}>
                    <span>52W Low</span>
                    <strong style={{ color: 'var(--red)' }}>${overview.week_low_52}</strong>
                  </div>
                </div>
                <p className={styles.overviewDesc}>{overview.description}</p>
              </div>
            )}

            {/* Top Movers */}
            {topMovers && (
              <div className={styles.moversCard}>
                <div className={styles.moversSection}>
                  <p className={styles.moversSectionTitle} style={{ color: 'var(--green)' }}>
                    🔥 Top Gainers
                  </p>
                  {topMovers.top_gainers.map(m => (
                    <MoverRow
                      key={m.ticker}
                      data={m}
                      onSelect={t => fetchStock(t)}
                    />
                  ))}
                </div>
                <div className={styles.moversDivider} />
                <div className={styles.moversSection}>
                  <p className={styles.moversSectionTitle} style={{ color: 'var(--red)' }}>
                    📉 Top Losers
                  </p>
                  {topMovers.top_losers.map(m => (
                    <MoverRow
                      key={m.ticker}
                      data={m}
                      onSelect={t => fetchStock(t)}
                    />
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
