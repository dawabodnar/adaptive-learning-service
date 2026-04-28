import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import styles from './Register.module.css';

export function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName || null,
        role: 'student',
      });

      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка реєстрації');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Реєстрація</h1>

        <label className={styles.label}>
          Імʼя
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className={styles.input}
            placeholder="Anna"
          />
        </label>

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
          {loading ? 'Створюю акаунт...' : 'Зареєструватись'}
        </button>

        <p className={styles.linkRow}>
          Вже маєш акаунт? <Link to="/login">Увійти</Link>
        </p>
      </form>
    </div>
  );
}