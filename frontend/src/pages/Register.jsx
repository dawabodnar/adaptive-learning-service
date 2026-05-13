import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './Register.module.css';

export function Register() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [budgetMinutes, setBudgetMinutes] = useState(30);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName || null,
        role: 'student',
        initial_time_budget_minutes: budgetMinutes,
      });
setError(null);
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const { data } = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      localStorage.setItem('access_token', data.access_token);
      setUser(data.user);
      navigate('/diagnostic');
  } catch (err) {
  if (err.response?.status === 409) {
    setError('Користувач з такою поштою вже існує. Спробуй увійти або використай інший email.');
  } else if (err.response?.status === 422) {
    setError('Перевір введені дані (email і пароль не менше 6 символів).');
  } else if (err.code === 'ERR_NETWORK' || !err.response) {
    setError('Сервер недоступний. Переконайся, що бекенд запущено.');
  } else {
    setError(err.response?.data?.detail ?? 'Помилка реєстрації. Спробуй ще раз.');
  }
}finally {
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

        <label className={styles.label}>
          Бажана тривалість сесії: <strong>{budgetMinutes} хв</strong>
          <input
            type="range"
            min={5}
            max={120}
            step={5}
            value={budgetMinutes}
            onChange={(e) => setBudgetMinutes(Number(e.target.value))}
            className={styles.range}
          />
          <small style={{ fontSize: 11, color: '#6b7280' }}>
            Це стартове значення. Далі система автоматично прогнозуватиме його за історією твоїх сесій.
          </small>
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
          {loading ? 'Створюю акаунт...' : 'Зареєструватись'}
        </button>

        <p className={styles.linkRow}>
          Вже маєш акаунт? <Link to="/login">Увійти</Link>
        </p>
      </form>
    </div>
  );
}