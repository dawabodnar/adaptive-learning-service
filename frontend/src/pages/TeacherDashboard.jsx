import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './TeacherDashboard.module.css';

export function TeacherDashboard() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [students, setStudents] = useState(null);
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
      api.get('/teacher/students')
        .then(({ data }) => setStudents(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [user]);

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!user || loading) return <div className={styles.loading}>Завантаження...</div>;
  if (!students) return null;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Кабінет викладача</h1>
          <p className={styles.subtitle}>{user.email}</p>
        </div>
        <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
      </header>

      <section className={styles.card}>
        <h2 className={styles.cardTitle}>Студенти ({students.length})</h2>

        {students.length === 0 ? (
          <p className={styles.empty}>Поки немає жодного студента.</p>
        ) : (
          <div className={styles.studentList}>
            {students.map((s) => (
              <StudentCard key={s.id} student={s} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function StudentCard({ student }) {
  const accuracyPercent = Math.round(student.accuracy * 100);
  const isLow = student.accuracy < 0.5;
  const hasData = student.total_answered > 0;

  return (
    <div className={styles.studentRow}>
      <div className={styles.studentHead}>
        <div className={styles.studentName}>
          {student.full_name || student.email}
        </div>
        <div className={styles.studentStats}>
          {student.total_sessions} сесій · {hasData ? `${accuracyPercent}% точність` : 'без даних'}
        </div>
      </div>

      {hasData && (
        <div className={styles.bar}>
          <div
            className={isLow ? styles.fillLow : styles.fillHigh}
            style={{ width: `${accuracyPercent}%` }}
          />
        </div>
      )}

      {student.weak_concepts.length > 0 && (
        <div className={styles.weakLine}>
          Слабкі теми: {student.weak_concepts.join(', ')}
        </div>
      )}
    </div>
  );
}