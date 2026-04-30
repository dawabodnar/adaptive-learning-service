import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './Profile.module.css';

export function Profile() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      api.get('/me')
        .then(({ data }) => setUser(data))
        .catch(() => navigate('/login'));
    }
  }, [user, setUser, navigate]);

  useEffect(() => {
    if (user) {
      api.get('/sessions/my-history')
        .then(({ data }) => setHistory(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [user]);

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!user || loading) return <div className={styles.loading}>Завантаження...</div>;
  if (!history) return null;

  const totalHours = Math.round((history.total_time_spent_seconds / 3600) * 10) / 10;
  const accuracyPercent = Math.round(history.overall_accuracy * 100);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Профіль</h1>
          <p className={styles.subtitle}>{user.email} · {translateRole(user.role)}</p>
        </div>
        <div className={styles.headerActions}>
          <Link to="/dashboard" className={styles.backLink}>Дашборд</Link>
          <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
        </div>
      </header>

      <section className={styles.userCard}>
        <div className={styles.avatar}>
          {(user.full_name || user.email).charAt(0).toUpperCase()}
        </div>
        <div className={styles.userInfo}>
          <h2 className={styles.userName}>{user.full_name || 'Без імені'}</h2>
          <p className={styles.userEmail}>{user.email}</p>
          <p className={styles.userMeta}>
            Зареєстровано: {new Date(user.created_at).toLocaleDateString('uk-UA')}
          </p>
        </div>
      </section>

      <section className={styles.statsGrid}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{history.total_sessions}</div>
          <div className={styles.statLabel}>Сесій</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{history.total_tasks_answered}</div>
          <div className={styles.statLabel}>Завдань</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{accuracyPercent}%</div>
          <div className={styles.statLabel}>Точність</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{totalHours} год</div>
          <div className={styles.statLabel}>Сумарно</div>
        </div>
      </section>

      <section className={styles.historyCard}>
        <h2 className={styles.cardTitle}>Останні сесії</h2>
        {history.sessions.length === 0 ? (
          <p className={styles.empty}>
            Ще немає жодної сесії. <Link to="/dashboard">Розпочати першу</Link>
          </p>
        ) : (
          <div className={styles.sessionList}>
            {history.sessions.map((s) => (
              <SessionRow key={s.session_id} session={s} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function SessionRow({ session }) {
  const accuracyPercent = Math.round(session.accuracy * 100);
  const isLow = session.accuracy < 0.5;
  const dateStr = session.started_at
    ? new Date(session.started_at).toLocaleDateString('uk-UA', {
        day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit',
      })
    : '';
  const minutes = Math.round(session.time_budget_seconds / 60);

  return (
    <div className={styles.sessionRow}>
      <div className={styles.sessionLeft}>
        <div className={styles.sessionTitle}>Сесія #{session.session_id}</div>
        <div className={styles.sessionMeta}>
          {dateStr} · {minutes} хв
          {!session.is_finished && <span className={styles.unfinished}> · не завершена</span>}
        </div>
      </div>
      <div className={isLow ? styles.accuracyLow : styles.accuracyHigh}>
        {session.answered}/{session.total_tasks} · {accuracyPercent}%
      </div>
    </div>
  );
}

function translateRole(role) {
  switch (role) {
    case 'student': return 'студент';
    case 'teacher': return 'викладач';
    case 'db_admin': return 'адмін БД';
    case 'system_admin': return 'адмін сервісу';
    default: return role;
  }
}