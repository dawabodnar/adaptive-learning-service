import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { ThemeToggle } from '../components/ThemeToggle';
import styles from './Results.module.css';

export function Results() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [sessionNumber, setSessionNumber] = useState(null);
  const [loading, setLoading] = useState(true);

  function handleLogout() {
    logout();
    navigate('/login');
  }

  useEffect(() => {
    Promise.all([
      api.get(`/sessions/${sessionId}/stats`),
      api.get('/sessions/my-history')
    ])
      .then(([statsRes, historyRes]) => {
        setStats(statsRes.data);
        // Знайти номер поточної сесії в історії
        const currentIndex = historyRes.data.sessions.findIndex(s => s.session_id === parseInt(sessionId));
        if (currentIndex !== -1) {
          setSessionNumber(historyRes.data.total_sessions - currentIndex);
        }
      })
      .catch((err) => {
        console.error(err);
        navigate('/dashboard');
      })
      .finally(() => setLoading(false));
  }, [sessionId, navigate]);

  if (loading) return <div className={styles.loading}>Завантаження...</div>;
  if (!stats) return null;

  const accuracyPercent = Math.round(stats.accuracy * 100);
  const avgTimeDisplay = stats.avg_time_per_task < 60 
    ? `${Math.round(stats.avg_time_per_task)} с` 
    : `${Math.round(stats.avg_time_per_task / 60 * 10) / 10} хв`;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>Результати сесії #{sessionNumber || stats.session_id}</h1>
        </div>
        <nav className={styles.headerNav}>
          <button onClick={() => navigate('/dashboard')} className={styles.navBtn}>
            Дашборд
          </button>
          <button onClick={() => navigate('/profile')} className={styles.navBtn}>
            Профіль
          </button>
          <ThemeToggle />
          <button onClick={handleLogout} className={styles.logoutBtn}>
            Вийти
          </button>
        </nav>
      </header>

      <section className={styles.metrics}>
        <div className={styles.metric}>
          <div className={styles.metricValue}>{stats.answered}/{stats.total_tasks}</div>
          <div className={styles.metricLabel}>Завдань виконано</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricValue}>{accuracyPercent}%</div>
          <div className={styles.metricLabel}>Правильних відповідей</div>
        </div>
        <div className={styles.metric}>
          <div className={styles.metricValue}>{avgTimeDisplay}</div>
          <div className={styles.metricLabel}>Середній час</div>
        </div>
      </section>

      {stats.by_concept.length > 0 && (
        <section className={styles.card}>
          <h2 className={styles.sectionTitle}>Розбивка по темах</h2>
          <div className={styles.conceptList}>
            {stats.by_concept.map((c) => {
              const accPercent = Math.round(c.accuracy * 100);
              const isWeak = c.accuracy < 0.5;
              return (
                <div key={c.concept_id} className={styles.conceptItem}>
                  <div className={styles.conceptHeader}>
                    <span className={styles.conceptName}>{c.concept_name}</span>
                    <span className={isWeak ? styles.accuracyLow : styles.accuracyHigh}>
                      {accPercent}% ({c.correct_count}/{c.tasks_count})
                    </span>
                  </div>
                  <div className={styles.conceptBar}>
                    <div
                      className={isWeak ? styles.conceptFillLow : styles.conceptFillHigh}
                      style={{ width: `${accPercent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {stats.weak_concepts.length > 0 && (
        <section className={styles.weakCard}>
          <h2 className={styles.sectionTitle}>Слабкі теми</h2>
          <p className={styles.weakDescription}>
            Над цими темами варто попрацювати додатково:
          </p>
          <ul className={styles.weakList}>
            {stats.weak_concepts.map((c) => (
              <li key={c.concept_id}>{c.concept_name}</li>
            ))}
          </ul>
        </section>
      )}

      <button onClick={() => navigate('/dashboard')} className={styles.continueBtn}>
        Розпочати нову сесію
      </button>
    </div>
  );
}