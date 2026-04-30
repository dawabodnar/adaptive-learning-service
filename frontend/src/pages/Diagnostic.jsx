import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './Diagnostic.module.css';

export function Diagnostic() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleStartTest() {
    setError(null);
    setLoading(true);
    try {
      // Стартуємо діагностичну сесію з малим бюджетом (10 хв)
      const { data } = await api.post('/sessions/start', {
        time_budget_seconds: 600,
      });
      navigate(`/session/${data.session_id}`, {
        state: { sessionData: data, isDiagnostic: true },
      });
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Не вдалося стартувати тест');
      setLoading(false);
    }
  }

  function handleSkip() {
    navigate('/dashboard');
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Як визначити твій початковий рівень?</h1>
        <p className={styles.subtitle}>
          {user ? `Привіт, ${user.full_name || user.email}!` : ''} Це допоможе системі підібрати завдання саме під тебе.
          Без цього ми поставимо середній рівень за замовчуванням, але адаптація запрацює пізніше.
        </p>

        <div className={styles.options}>
          <button
            type="button"
            onClick={handleStartTest}
            className={`${styles.option} ${styles.recommended}`}
            disabled={loading}
          >
            <div className={styles.badge}>Рекомендовано</div>
            <h3 className={styles.optionTitle}>Пройти короткий тест</h3>
            <p className={styles.optionText}>
              Близько 10 хв. Точніший підбір завдань з першої справжньої сесії.
            </p>
          </button>

          <button
            type="button"
            onClick={handleSkip}
            className={styles.option}
            disabled={loading}
          >
            <h3 className={styles.optionTitle}>Пропустити</h3>
            <p className={styles.optionText}>
              Стартуєш зі середнім рівнем. Система швидко відкоригує під тебе після кількох сесій.
            </p>
          </button>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <button
          type="button"
          onClick={handleStartTest}
          className={styles.primaryBtn}
          disabled={loading}
        >
          {loading ? 'Готую тест...' : 'Пройти тест'}
        </button>
        <button
          type="button"
          onClick={handleSkip}
          className={styles.ghostBtn}
          disabled={loading}
        >
          Пропустити
        </button>
      </div>
    </div>
  );
}