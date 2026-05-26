import { useState, useEffect } from "react";
import { getPrediction, getHistory, getComparison } from "./api";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";
import { TrendingUp, TrendingDown, Search, RefreshCw } from "lucide-react";
import "./App.css";

// ── Comparison Card ──────────────────────────────────────
function CompareCard({ data }) {
  const up = data.change_pct >= 0;
  return (
    <div className={`compare-card ${up ? "up" : "down"}`}>
      <span className="compare-ticker">{data.ticker}</span>
      <span className="compare-price">${data.predicted_price}</span>
      <span className="compare-pct">
        {up ? "▲" : "▼"} {Math.abs(data.change_pct)}%
      </span>
    </div>
  );
}

// ── Custom Tooltip ───────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-date">{label}</p>
        <p className="tooltip-price">${payload[0].value}</p>
      </div>
    );
  }
  return null;
}

// ── Main App ─────────────────────────────────────────────
export default function App() {
  const [ticker,     setTicker]     = useState("AAPL");
  const [input,      setInput]      = useState("AAPL");
  const [prediction, setPrediction] = useState(null);
  const [history,    setHistory]    = useState([]);
  const [comparisons,setComparisons]= useState([]);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState(null);

  // Fetch prediction + history whenever ticker changes
  useEffect(() => {
    fetchData(ticker);
    fetchComparisons();
  }, [ticker]);

  const fetchData = async (t) => {
    setLoading(true);
    setError(null);
    try {
      const [predRes, histRes] = await Promise.all([
        getPrediction(t),
        getHistory(t, 90)
      ]);

      setPrediction(predRes.data);

      // Format history for chart
      const chartData = histRes.data.dates.map((date, i) => ({
        date,
        price: histRes.data.prices[i]
      }));

      // Add prediction point at the end
      const lastDate = new Date(histRes.data.dates.at(-1));
      lastDate.setDate(lastDate.getDate() + 1);
      chartData.push({
        date      : lastDate.toISOString().split("T")[0],
        price     : null,
        prediction: histRes.data.prediction
      });

      setHistory(chartData);
    } catch (err) {
      setError("Could not fetch data. Check ticker symbol.");
    }
    setLoading(false);
  };

  const fetchComparisons = async () => {
    try {
      const res = await getComparison(["AAPL", "MSFT", "GOOGL", "TSLA"]);
      setComparisons(res.data.comparisons);
    } catch (_) {}
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (input.trim()) setTicker(input.trim().toUpperCase());
  };

  const isUp = prediction && prediction.change >= 0;

  return (
    <div className="app">

      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <h1 className="logo">📈 StockMind <span>AI</span></h1>
          <p className="tagline">LSTM-powered predictions</p>
        </div>
        <form className="search-form" onSubmit={handleSearch}>
          <input
            className="search-input"
            value={input}
            onChange={e => setInput(e.target.value.toUpperCase())}
            placeholder="Enter ticker..."
            maxLength={5}
          />
          <button className="search-btn" type="submit">
            <Search size={18} />
          </button>
        </form>
      </header>

      <main className="main">

        {/* ── Error ── */}
        {error && <div className="error-banner">{error}</div>}

        {/* ── Prediction Card ── */}
        {prediction && (
          <div className={`prediction-card ${isUp ? "up" : "down"}`}>
            <div className="pred-left">
              <p className="pred-label">Next Day Prediction</p>
              <h2 className="pred-ticker">{prediction.ticker}</h2>
              <p className="pred-current">
                Current: <strong>${prediction.current_price}</strong>
              </p>
            </div>
            <div className="pred-right">
              <p className="pred-price">${prediction.predicted_price}</p>
              <div className="pred-change">
                {isUp
                  ? <TrendingUp size={20} />
                  : <TrendingDown size={20} />}
                <span>
                  {isUp ? "+" : ""}{prediction.change} ({prediction.change_pct}%)
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ── Chart ── */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>90-Day Price History + Prediction</h3>
            {loading && <RefreshCw size={16} className="spin" />}
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={history}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                tickFormatter={d => d.slice(5)}
                interval={14}
              />
              <YAxis
                tick={{ fill: "#94a3b8", fontSize: 11 }}
                domain={["auto", "auto"]}
                tickFormatter={v => `$${v}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine
                x={history.at(-1)?.date}
                stroke="#f59e0b"
                strokeDasharray="4 4"
                label={{ value: "Pred", fill: "#f59e0b", fontSize: 11 }}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#6366f1"
                strokeWidth={2}
                fill="url(#colorPrice)"
                connectNulls={false}
                dot={false}
              />
              <Area
                type="monotone"
                dataKey="prediction"
                stroke="#f59e0b"
                strokeWidth={0}
                fill="#f59e0b"
                dot={{ r: 6, fill: "#f59e0b", strokeWidth: 2, stroke: "#fff" }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* ── Compare ── */}
        <div className="compare-section">
          <h3>Market Overview</h3>
          <div className="compare-grid">
            {comparisons.map(c => (
              !c.error && <CompareCard key={c.ticker} data={c} />
            ))}
          </div>
        </div>

      </main>
    </div>
  );
}