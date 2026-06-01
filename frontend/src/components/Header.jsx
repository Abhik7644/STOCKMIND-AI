import { useState }   from 'react';
import { useNavigate } from 'react-router-dom';
import { useStock }    from '../context/StockContext';
import { Search, Bell, Zap } from 'lucide-react';
import styles from './Header.module.css';

export default function Header({ title }) {
  const [query,    setQuery]    = useState('');
  const [training, setTraining] = useState(false);
  const { fetchStock }          = useStock();
  const navigate                = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    const ticker = query.trim().toUpperCase();
    setQuery('');
    setTraining(true);
    await fetchStock(ticker);
    setTraining(false);
    navigate('/predictions');
  };

  return (
    <header className={styles.header}>
      <h2 className={styles.title}>{title}</h2>

      <div className={styles.right}>

        {/* Search */}
        <form className={styles.searchForm} onSubmit={handleSearch}>
          <Search size={14} className={styles.searchIcon} />
          <input
            className={styles.searchInput}
            value={query}
            onChange={e => setQuery(e.target.value.toUpperCase())}
            placeholder="Search ticker…"
            maxLength={5}
          />
          {training && (
            <span className={styles.trainingBadge}>
              <Zap size={10} /> Training…
            </span>
          )}
        </form>

        {/* Notification bell */}
        <button className={styles.iconBtn}>
          <Bell size={16} />
          <span className={styles.notifDot} />
        </button>

      </div>
    </header>
  );
}
