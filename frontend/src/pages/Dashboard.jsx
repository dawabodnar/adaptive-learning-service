import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { ThemeToggle } from '../components/ThemeToggle';
import styles from './Dashboard.module.css';

export function Dashboard() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [suggestion, setSuggestion] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      api.get('/me')
        .then(({ data }) => setUser(data))
        .catch(() => navigate('/login'));
    }
  }, [user, setUser, navigate]);

  useEffect(() => {
    if (user) {
      api.get('/sessions/suggested-budget')
        .then(({ data }) => setSuggestion(data))
        .catch(console.error);
    }
  }, [user]);

  async function handleStartSession() {
    if (!suggestion) return;
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post('/sessions/start', {
        time_budget_seconds: suggestion.time_budget_seconds,
      });
      navigate(`/session/${data.session_id}`, { state: { sessionData: data } });
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Не вдалося стартувати сесію');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!user) return <div className={styles.loading}>Завантаження...</div>;

  const minutes = suggestion ? Math.round(suggestion.time_budget_seconds / 60) : null;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Адаптивне навчання</h1>
          <p className={styles.subtitle}>Привіт, {user.full_name || user.email}</p>
        </div>
        <div className={styles.headerActions}>
          <ThemeToggle />
          <Link to="/profile" className={styles.profileLink}>Профіль</Link>
          <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
        </div>
      </header>

      <main className={styles.card}>
        <h2 className={styles.cardTitle}>Готова до навчальної сесії?</h2>

        {suggestion && (
          <div className={styles.budgetBlock}>
            <div className={styles.budgetLabel}>Бюджет часу на цю сесію</div>
            <div className={styles.budgetValue}>{minutes} хв</div>
            <div className={styles.budgetSource}>{suggestion.explanation}</div>
          </div>
        )}

        {!suggestion && (
          <div className={styles.budgetBlock}>
            <div className={styles.budgetLabel}>Розраховуємо бюджет часу...</div>
          </div>
        )}

        {error && <div className={styles.error}>{error}</div>}

        <button
          onClick={handleStartSession}
          className={styles.startBtn}
          disabled={loading || !suggestion}
        >
          {loading ? 'Підбираємо завдання...' : 'Почати сесію'}
        </button>
      </main>
    </div>
  );
}