import { useState }   from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth }     from '../context/AuthContext';
import styles          from './Login.module.css';

export default function Login() {
  const [tab,      setTab]      = useState('login');
  const [email,    setEmail]    = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handle = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'login') {
        await login(email, password);
      } else {
        await register(email, username, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.');
    }
    setLoading(false);
  };

  return (
    <div className={styles.page}>
      {/* Background grid */}
      <div className={styles.grid} />

      <div className={styles.card}>
        <div className={styles.logo}>
          <span className={styles.logoMark}>◈</span>
          <div>
            <h1 className={styles.logoTitle}>StockMind</h1>
            <p className={styles.logoSub}>AI — LSTM Predictions</p>
          </div>
        </div>

        <div className={styles.tabs}>
          <button
            className={tab === 'login' ? styles.tabActive : styles.tabInactive}
            onClick={() => setTab('login')}
          >Login</button>
          <button
            className={tab === 'register' ? styles.tabActive : styles.tabInactive}
            onClick={() => setTab('register')}
          >Register</button>
        </div>

        <form onSubmit={handle} className={styles.form}>
          <div className={styles.field}>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          {tab === 'register' && (
            <div className={styles.field}>
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="yourname"
                required
              />
            </div>
          )}

          <div className={styles.field}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <button
            type="submit"
            className={styles.submit}
            disabled={loading}
          >
            {loading ? 'Please wait…' : tab === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className={styles.hint}>
          Powered by LSTM · Real market data · Alpha Vantage
        </p>
      </div>
    </div>
  );
}
