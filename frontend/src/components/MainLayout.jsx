import { useState } from 'react';
import { Outlet }   from 'react-router-dom';
import Sidebar       from './Sidebar';
import styles        from './MainLayout.module.css';

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className={styles.layout}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(c => !c)} />
      <div className={`${styles.main} ${collapsed ? styles.collapsed : ''}`}>
        <Outlet />
      </div>
    </div>
  );
}
