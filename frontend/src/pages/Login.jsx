import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './Login.module.css';

export function Login() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const { data } = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

localStorage.setItem('access_token', data.access_token);
setUser(data.user);
// Переадресація залежно від ролі
if (data.user.role === 'teacher') {
  navigate('/teacher');
} else if (data.user.role === 'db_admin') {
  navigate('/admin/db');
} else if (data.user.role === 'system_admin') {
  navigate('/admin/users');
} else {
  navigate('/dashboard');
}
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка входу');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Вхід</h1>

        <label className={styles.label}>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={styles.input}
            placeholder="anna@test.com"
          />
        </label>

        <label className={styles.label}>
          Пароль
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className={styles.input}
          />
        </label>

        {error && <div className={styles.error}>{error}</div>}

        <button type="submit" className={styles.button} disabled={loading}>
          {loading ? 'Входжу...' : 'Увійти'}
        </button>

        <p className={styles.linkRow}>
          Немає акаунту? <Link to="/register">Зареєструватись</Link>
        </p>
      </form>
    </div>
  );
}