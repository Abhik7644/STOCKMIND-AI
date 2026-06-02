import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, getProfile } from '../api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [token,   setToken]   = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      getProfile()
        .then(r => setUser(r.data))
        .catch(() => logout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);   // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (email, password) => {
    const res = await loginUser(email, password);
    const t   = res.data.access_token;
    localStorage.setItem('token', t);
    setToken(t);
    const profile = await getProfile();
    setUser(profile.data);
  };

  const register = async (email, username, password) => {
    const res = await registerUser(email, username, password);
    const t   = res.data.access_token;
    localStorage.setItem('token', t);
    setToken(t);
    const profile = await getProfile();
    setUser(profile.data);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
