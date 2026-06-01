import { NavLink } from 'react-router-dom';
import { useAuth }  from '../context/AuthContext';
import styles       from './Sidebar.module.css';
import {
  LayoutDashboard, TrendingUp, Brain,
  Briefcase, Settings, LogOut, LogIn
} from 'lucide-react';

const NAV = [
  { to: '/',           icon: LayoutDashboard, label: 'Dashboard'   },
  { to: '/market',     icon: TrendingUp,      label: 'Market'      },
  { to: '/predictions',icon: Brain,           label: 'AI Predict'  },
  { to: '/portfolio',  icon: Briefcase,       label: 'Portfolio'   },
  { to: '/settings',   icon: Settings,        label: 'Settings'    },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className={styles.sidebar}>

      {/* Logo */}
      <div className={styles.logo}>
        <span className={styles.logoIcon}>◈</span>
        <div>
          <p className={styles.logoName}>StockMind</p>
          <p className={styles.logoSub}>AI</p>
        </div>
      </div>

      {/* Nav */}
      <nav className={styles.nav}>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className={styles.bottom}>
        {user ? (
          <>
            <div className={styles.userCard}>
              <div className={styles.avatar}>
                {user.username?.[0]?.toUpperCase()}
              </div>
              <div className={styles.userInfo}>
                <p className={styles.userName}>{user.username}</p>
                <p className={styles.userBalance}>
                  ${user.paper_balance?.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
            <button className={styles.logoutBtn} onClick={logout}>
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          </>
        ) : (
          <NavLink to="/login" className={styles.loginBtn}>
            <LogIn size={14} />
            <span>Login</span>
          </NavLink>
        )}
      </div>

    </aside>
  );
}
