import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth }  from './context/AuthContext';
import { StockProvider }          from './context/StockContext';
import MainLayout                 from './components/MainLayout';
import Login                      from './pages/Login';
import Dashboard                  from './pages/Dashboard';
import AIPredictions              from './pages/AIPredictions';
import Portfolio                  from './pages/Portfolio';
import Settings                   from './pages/Settings';
import './globals.css';

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return (
    <div style={{
      minHeight: '100vh', background: 'var(--bg-base)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: 'var(--text-secondary)', fontFamily: 'var(--font-display)'
    }}>
      Loading…
    </div>
  );
  return token ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index           element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"  element={<Dashboard />} />
        <Route path="predictions" element={<AIPredictions />} />
        <Route path="portfolio"  element={<Portfolio />} />
        <Route path="settings"   element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <StockProvider>
          <AppRoutes />
        </StockProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
