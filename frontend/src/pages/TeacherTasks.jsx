import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './TeacherTasks.module.css';
import { ThemeToggle } from '../components/ThemeToggle';

export function TeacherTasks() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [tasks, setTasks] = useState([]);
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState(null);

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
      api.get('/teacher/tasks'),
      api.get('/teacher/concepts'),
    ])
      .then(([tasksRes, conceptsRes]) => {
        setTasks(tasksRes.data);
        setConcepts(conceptsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleArchive(taskId) {
    if (!confirm('Ви впевнені що хочете архівувати це завдання?')) return;
    try {
      await api.delete(`/teacher/tasks/${taskId}`);
      loadData();
    } catch (err) {
      alert('Помилка: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    }
  }

  async function handleSaveEdit(taskId, updates) {
    try {
      await api.patch(`/teacher/tasks/${taskId}`, updates);
      setEditingTaskId(null);
      loadData();
    } catch (err) {
      alert('Помилка при редагуванні: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
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
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>Керування завданнями</h1>
          <p className={styles.subtitle}>{user.email}</p>
        </div>
        <nav className={styles.headerNav}>
          <button 
            onClick={() => navigate('/teacher')} 
            className={styles.navBtn}
          >
            📊 Статистика
          </button>
          <button 
            className={`${styles.navBtn} ${styles.active}`}
            disabled
          >
            ✓ Завдання
          </button>
          <div className={styles.divider}></div>
          <ThemeToggle />
          <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
        </nav>
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
              <div key={t.id}>
                {editingTaskId === t.id ? (
                  <EditTaskForm
                    task={t}
                    concepts={concepts}
                    onSave={handleSaveEdit}
                    onCancel={() => setEditingTaskId(null)}
                  />
                ) : (
                  <div className={`${styles.taskRow} ${!t.is_active ? styles.archived : ''}`}>
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
                      <div className={styles.taskActions}>
                        <button onClick={() => setEditingTaskId(t.id)} className={styles.editBtn}>
                          Редагувати
                        </button>
                        <button onClick={() => handleArchive(t.id)} className={styles.deleteBtn}>
                          Архівувати
                        </button>
                      </div>
                    )}
                  </div>
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
  const [answerType, setAnswerType] = useState('text');

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.post('/teacher/tasks', {
        content,
        correct_answer: answer,
        difficulty: Number(difficulty),
        discrimination: 1.0,
        guessing: 0.25,
        estimated_time_seconds: Number(time),
        answer_type: answerType,
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
    Тип відповіді
    <select
      value={answerType}
      onChange={(e) => setAnswerType(e.target.value)}
      className={styles.input}
    >
      <option value="text">Текст</option>
      <option value="number">Число</option>
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

function EditTaskForm({ task, concepts, onSave, onCancel }) {
  const [content, setContent] = useState(task.content);
  const [answer, setAnswer] = useState(task.correct_answer);
  const [difficulty, setDifficulty] = useState(task.difficulty);
  const [time, setTime] = useState(task.estimated_time_seconds);
  const [answerType, setAnswerType] = useState(task.answer_type);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await onSave(task.id, {
        content,
        correct_answer: answer,
        difficulty: Number(difficulty),
        estimated_time_seconds: Number(time),
        answer_type: answerType,
      });
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={`${styles.form} ${styles.editForm}`}>
      <label className={styles.label}>
        Текст завдання
        <input
          type="text"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
          minLength={3}
          className={styles.input}
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
          />
        </label>

        <label className={styles.label}>
          Тип відповіді
          <select
            value={answerType}
            onChange={(e) => setAnswerType(e.target.value)}
            className={styles.input}
          >
            <option value="text">Текст</option>
            <option value="number">Число</option>
          </select>
        </label>
      </div>

      <div className={styles.formRow}>
        <label className={styles.label}>
          Складність b ({Number(difficulty).toFixed(1)})
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

      <div className={styles.formActions}>
        <button type="submit" className={styles.saveBtn} disabled={saving}>
          {saving ? 'Зберігаю...' : 'Зберегти'}
        </button>
        <button type="button" onClick={onCancel} className={styles.cancelBtn}>
          Скасувати
        </button>
      </div>
    </form>
  );
}