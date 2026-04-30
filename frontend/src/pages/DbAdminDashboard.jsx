import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './DbAdminDashboard.module.css';

export function DbAdminDashboard() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [tasks, setTasks] = useState([]);
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (!user) {
      api.get('/me')
        .then(({ data }) => setUser(data))
        .catch(() => navigate('/login'));
    }
  }, [user, setUser, navigate]);

  useEffect(() => {
    if (user) loadData();
  }, [user]);

  function loadData() {
    setLoading(true);
    Promise.all([
      api.get('/admin/db/tasks'),
      api.get('/admin/db/concepts'),
    ])
      .then(([tasksRes, conceptsRes]) => {
        setTasks(tasksRes.data);
        setConcepts(conceptsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleArchive(taskId) {
    if (!confirm('Архівувати це завдання?')) return;
    try {
      await api.delete(`/admin/db/tasks/${taskId}`);
      loadData();
    } catch (err) {
      alert('Помилка: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!user || loading) return <div className={styles.loading}>Завантаження...</div>;

  const activeCount = tasks.filter((t) => t.is_active).length;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Адміністрування БД</h1>
          <p className={styles.subtitle}>{user.email}</p>
        </div>
        <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
      </header>

      <section className={styles.card}>
        <div className={styles.cardHead}>
          <h2 className={styles.cardTitle}>
            Завдання ({activeCount} активних / {tasks.length} всього)
          </h2>
          <button onClick={() => setShowForm(!showForm)} className={styles.addBtn}>
            {showForm ? 'Сховати форму' : '+ Додати завдання'}
          </button>
        </div>

        {showForm && (
          <TaskForm
            concepts={concepts}
            onCreated={() => {
              setShowForm(false);
              loadData();
            }}
          />
        )}

        {tasks.length === 0 ? (
          <p className={styles.empty}>База завдань порожня.</p>
        ) : (
          <div className={styles.taskList}>
            {tasks.map((t) => (
              <div key={t.id} className={`${styles.taskRow} ${!t.is_active ? styles.archived : ''}`}>
                <div className={styles.taskMain}>
                  <div className={styles.taskContent}>
                    {t.content}
                    {!t.is_active && <span className={styles.archivedBadge}>архівовано</span>}
                  </div>
                  <div className={styles.taskMeta}>
                    {t.concept_names.map((name, i) => (
                      <span key={i} className={styles.tag}>{name}</span>
                    ))}
                    <span>складність {t.difficulty.toFixed(2)}</span>
                    <span>·</span>
                    <span>{t.estimated_time_seconds} с</span>
                  </div>
                </div>
                {t.is_active && (
                  <button onClick={() => handleArchive(t.id)} className={styles.deleteBtn}>
                    Архівувати
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function TaskForm({ concepts, onCreated }) {
  const [content, setContent] = useState('');
  const [answer, setAnswer] = useState('');
  const [difficulty, setDifficulty] = useState(0);
  const [time, setTime] = useState(120);
  const [conceptId, setConceptId] = useState(concepts[0]?.id ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.post('/admin/db/tasks', {
        content,
        correct_answer: answer,
        difficulty: Number(difficulty),
        discrimination: 1.0,
        guessing: 0.25,
        estimated_time_seconds: Number(time),
        concepts: conceptId ? [{ concept_id: Number(conceptId), weight: 1.0 }] : [],
      });
      setContent('');
      setAnswer('');
      onCreated();
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <label className={styles.label}>
        Текст завдання
        <input
          type="text"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          minLength={3}
          className={styles.input}
          placeholder="Розвʼяжіть рівняння: 5x + 10 = 0"
        />
      </label>

      <div className={styles.formRow}>
        <label className={styles.label}>
          Правильна відповідь
          <input
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            required
            className={styles.input}
            placeholder="-2"
          />
        </label>

        <label className={styles.label}>
          Концепт
          <select
            value={conceptId}
            onChange={(e) => setConceptId(e.target.value)}
            className={styles.input}
          >
            {concepts.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </label>
      </div>

      <div className={styles.formRow}>
        <label className={styles.label}>
          Складність b ({difficulty})
          <input
            type="range"
            min={-2}
            max={2}
            step={0.1}
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className={styles.range}
          />
        </label>

        <label className={styles.label}>
          Орієнтовний час, с
          <input
            type="number"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            min={10}
            max={3600}
            className={styles.input}
          />
        </label>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Зберігаю...' : 'Створити завдання'}
      </button>
    </form>
  );
}