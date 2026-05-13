import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
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

  function redirectByRole(role) {
    if (role === 'teacher') navigate('/teacher');
    else if (role === 'system_admin') navigate('/admin/users');
    else navigate('/dashboard');
  }

  function handleError(err, fallback) {
    if (err.response?.status === 401) {
      setError('Невірний email або пароль. Перевір дані і спробуй ще раз.');
    } else if (err.response?.status === 403) {
      setError('Цей акаунт заблоковано адміністратором.');
    } else if (err.response?.status === 422) {
      setError('Перевір формат email — має бути на кшталт name@example.com.');
    } else if (err.code === 'ERR_NETWORK' || !err.response) {
      setError('Сервер недоступний. Переконайся, що бекенд запущено (uvicorn).');
    } else {
      setError(err.response?.data?.detail ?? fallback);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const { data } = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      setError(null);
      localStorage.setItem('access_token', data.access_token);
      setUser(data.user);
      redirectByRole(data.user.role);
    } catch (err) {
      handleError(err, 'Помилка входу. Спробуй ще раз.');
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse) {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/google', {
        credential: credentialResponse.credential,
      });
      setError(null);
      localStorage.setItem('access_token', data.access_token);
      setUser(data.user);
      redirectByRole(data.user.role);
    } catch (err) {
      handleError(err, 'Помилка входу через Google.');
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

        {error && (
          <div className={styles.error}>
            <span className={styles.errorText}>{error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className={styles.errorClose}
              aria-label="Закрити повідомлення"
            >
              ×
            </button>
          </div>
        )}

        <button type="submit" className={styles.button} disabled={loading}>
          {loading ? 'Входжу...' : 'Увійти'}
        </button>

        <div className={styles.divider}>
          <span>або</span>
        </div>

        <div className={styles.googleWrap}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google авторизація не вдалася')}
            theme="outline"
            size="large"
            text="continue_with"
            locale="uk"
            width="320"
          />
        </div>

        <p className={styles.linkRow}>
          Немає акаунту? <Link to="/register">Зареєструватись</Link>
        </p>
        <p className={styles.linkRow}>
          Або <Link to="/guest">спробуй без реєстрації</Link>
        </p>
      </form>
    </div>
  );
}