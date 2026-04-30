import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import styles from './Session.module.css';

export function Session() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // Дані сесії приходять через navigation state із Dashboard
  const sessionData = location.state?.sessionData;

  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [results, setResults] = useState([]); // {task_id, is_correct}
  const [loading, setLoading] = useState(false);
  const [taskStartTime, setTaskStartTime] = useState(Date.now());

  useEffect(() => {
    if (!sessionData) {
      navigate('/dashboard');
    }
  }, [sessionData, navigate]);

  if (!sessionData) return null;

  const tasks = sessionData.tasks;
  const currentTask = tasks[currentIndex];
  const isLast = currentIndex === tasks.length - 1;

  async function handleSubmitAnswer() {
    if (!answer.trim()) return;
    setLoading(true);

    const timeSpent = Math.round((Date.now() - taskStartTime) / 1000);

    try {
      const { data } = await api.post(`/sessions/${sessionId}/answer`, {
        task_id: currentTask.id,
        answer: answer.trim(),
        time_spent_seconds: timeSpent,
      });

      setResults((prev) => [...prev, data]);
      setAnswer('');

      if (isLast) {
        // Завершуємо сесію і йдемо на результати
        await api.post(`/sessions/${sessionId}/finish`);
        navigate(`/results/${sessionId}`);
      } else {
        setCurrentIndex(currentIndex + 1);
        setTaskStartTime(Date.now());
      }
    } catch (err) {
      console.error(err);
      alert('Помилка відправки відповіді: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.progress}>
          Завдання {currentIndex + 1} з {tasks.length}
        </div>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${((currentIndex + 1) / tasks.length) * 100}%` }}
          />
        </div>
      </header>

      <main className={styles.card}>
        <h2 className={styles.taskTitle}>{currentTask.content}</h2>
        <p className={styles.timeHint}>
          Орієнтовний час: {currentTask.estimated_time_seconds} с
        </p>

        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !loading) handleSubmitAnswer();
          }}
          className={styles.input}
          placeholder="Введіть відповідь"
          autoFocus
        />

        <button
          onClick={handleSubmitAnswer}
          className={styles.submitBtn}
          disabled={loading || !answer.trim()}
        >
          {loading ? 'Перевіряю...' : isLast ? 'Завершити сесію' : 'Далі'}
        </button>

        {results.length > 0 && (
          <div className={styles.history}>
            <h3 className={styles.historyTitle}>Попередні відповіді</h3>
            <div className={styles.historyList}>
              {results.map((r, idx) => (
                <div key={idx} className={r.is_correct ? styles.correct : styles.incorrect}>
                  Завдання {idx + 1}: {r.is_correct ? '✓ правильно' : '✗ помилка'}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}