import Header from '../components/Header';
import { useAuth } from '../context/AuthContext';
import styles from './Settings.module.css';

export default function Settings() {
  const { user, logout } = useAuth();
  return (
    <div className={styles.page}>
      <Header title="Settings" />
      <div className={styles.body}>

        <div className={styles.card}>
          <h3>Profile</h3>
          {user ? (
            <div className={styles.profileGrid}>
              <div className={styles.profileItem}>
                <span>Username</span>
                <strong>{user.username}</strong>
              </div>
              <div className={styles.profileItem}>
                <span>Email</span>
                <strong>{user.email}</strong>
              </div>
              <div className={styles.profileItem}>
                <span>Paper Balance</span>
                <strong style={{ color: 'var(--green)' }}>
                  ${user.paper_balance?.toFixed(2)}
                </strong>
              </div>
              <div className={styles.profileItem}>
                <span>Member Since</span>
                <strong>
                  {user.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : '—'}
                </strong>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)' }}>Not logged in.</p>
          )}
        </div>

        <div className={styles.card}>
          <h3>About This Project</h3>
          <div className={styles.aboutGrid}>
            {[
              { label: 'Model',      value: '2-Layer LSTM' },
              { label: 'Framework',  value: 'TensorFlow / Keras' },
              { label: 'Backend',    value: 'FastAPI + SQLModel' },
              { label: 'Frontend',   value: 'React + CSS Modules' },
              { label: 'Market Data',value: 'yfinance + Alpha Vantage' },
              { label: 'Accuracy',   value: 'MAPE 2.85%' },
            ].map(({ label, value }) => (
              <div key={label} className={styles.aboutItem}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </div>

        {user && (
          <button className={styles.logoutBtn} onClick={logout}>
            Sign Out
          </button>
        )}
      </div>
    </div>
  );
}
