import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './Dashboard.module.css';

export function Dashboard() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();

  const [useCustomTime, setUseCustomTime] = useState(false);
  const [customMinutes, setCustomMinutes] = useState(30);
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

  const autoMinutes = suggestion ? Math.round(suggestion.time_budget_seconds / 60) : 30;
  const effectiveSeconds = useCustomTime ? customMinutes * 60 : (suggestion?.time_budget_seconds ?? 1800);

  async function handleStartSession() {
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post('/sessions/start', {
        time_budget_seconds: effectiveSeconds,
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

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Адаптивне навчання</h1>
          <p className={styles.subtitle}>Привіт, {user.full_name || user.email}</p>
        </div>
        <div className={styles.headerActions}>
          <Link to="/profile" className={styles.profileLink}>Профіль</Link>
          <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
        </div>
      </header>

      <main className={styles.card}>
        <h2 className={styles.cardTitle}>Розпочати навчальну сесію</h2>
        <p className={styles.description}>
          Якщо хочеш — задай свій час. Інакше система визначить його автоматично.
        </p>

        <div className={styles.toggleRow}>
          <button
            type="button"
            onClick={() => setUseCustomTime(!useCustomTime)}
            className={`${styles.toggle} ${useCustomTime ? styles.toggleOn : ''}`}
          >
            <span className={styles.toggleKnob} />
          </button>
          <div>
            <div className={styles.toggleLabel}>Задати час самостійно</div>
            <div className={styles.toggleHint}>
              {useCustomTime ? 'Користувач керує тривалістю' : 'Час визначається автоматично'}
            </div>
          </div>
        </div>

        {!useCustomTime && suggestion && (
          <div className={styles.autoInfo}>
            <div className={styles.autoIcon}>i</div>
            <div className={styles.autoText}>
              {suggestion.source === 'history' ? (
                <>Система розрахувала <strong>T = {autoMinutes} хв</strong> на основі <strong>{suggestion.based_on_sessions} попередніх сесій</strong>.</>
              ) : (
                <>Це твоя перша сесія — використовуємо <strong>стандартне значення T = 30 хв</strong>. Після кількох сесій система прогнозуватиме час на основі історії.</>
              )}
            </div>
          </div>
        )}

        <div className={`${styles.rangeBlock} ${!useCustomTime ? styles.rangeDisabled : ''}`}>
          <label className={styles.label}>
            Бюджет часу:{' '}
            <strong>
              {useCustomTime ? `${customMinutes} хв` : `${autoMinutes} хв (авто)`}
            </strong>
            <input
              type="range"
              min={5}
              max={120}
              step={5}
              value={useCustomTime ? customMinutes : autoMinutes}
              onChange={(e) => setCustomMinutes(Number(e.target.value))}
              disabled={!useCustomTime}
              className={styles.range}
            />
            <div className={styles.rangeMarks}>
              <span>5 хв</span>
              <span>120 хв</span>
            </div>
          </label>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <button onClick={handleStartSession} className={styles.startBtn} disabled={loading}>
          {loading ? 'Підбираємо завдання...' : 'Сформувати сесію'}
        </button>
      </main>
    </div>
  );
}