import { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import styles from './Session.module.css';

export function Session() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const sessionData = location.state?.sessionData;
  const hasFinishedRef = useRef(false);
  const submittingRef = useRef(false);
  const answerRef = useRef('');
  const currentTaskRef = useRef(null);
  const taskStartTimeRef = useRef(Date.now());

  const [currentIndex, setCurrentIndex] = useState(() => {
    const saved = sessionStorage.getItem(`session_${sessionId}_index`);
    return saved ? parseInt(saved) : 0;
  });

  const [results, setResults] = useState(() => {
    const saved = sessionStorage.getItem(`session_${sessionId}_results`);
    return saved ? JSON.parse(saved) : [];
  });

  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskStartTime, setTaskStartTime] = useState(Date.now());
  const inputRef = useRef(null);
  const [endTime, setEndTime] = useState(null);
  const [now, setNow] = useState(Date.now());

  // Синхронізуємо answer → ref
  useEffect(() => {
    answerRef.current = answer;
  }, [answer]);

  // Зберігаємо індекс
  useEffect(() => {
    sessionStorage.setItem(`session_${sessionId}_index`, currentIndex);
  }, [currentIndex, sessionId]);

  // Зберігаємо results
  useEffect(() => {
    sessionStorage.setItem(`session_${sessionId}_results`, JSON.stringify(results));
  }, [results, sessionId]);

  useEffect(() => {
    if (sessionData?.end_time) {
      setEndTime(new Date(sessionData.end_time).getTime());
      setNow(Date.now());
    }
  }, [sessionData]);

  useEffect(() => {
    if (!endTime) return;
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, [endTime]);

  useEffect(() => {
    if (!sessionData) navigate('/dashboard');
  }, [sessionData, navigate]);

  useEffect(() => {
    if (inputRef.current) inputRef.current.focus();
  }, [currentIndex]);

  const remaining = endTime ? Math.max(0, endTime - now) : null;
  const isTimeUp = remaining !== null && remaining <= 0;

  useEffect(() => {
    if (!isTimeUp) return;
    if (hasFinishedRef.current) return;
    finishSessionAutomatically();
  }, [isTimeUp]);

  function formatTime(ms) {
    const total = Math.max(0, Math.floor(ms / 1000));
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  async function finishSessionAutomatically() {
    if (hasFinishedRef.current) return;
    hasFinishedRef.current = true;

    const currentAnswer = answerRef.current;
    const task = currentTaskRef.current;

    if (currentAnswer.trim() && task && !submittingRef.current) {
      try {
        await api.post(`/sessions/${sessionId}/answer`, {
          task_id: task.id,
          answer: currentAnswer.trim(),
          time_spent_seconds: Math.round((Date.now() - taskStartTimeRef.current) / 1000),
        });
      } catch (e) {
        console.error('Auto-submit failed:', e);
      }
    }

    try {
      await api.post(`/sessions/${sessionId}/finish`);
      sessionStorage.removeItem(`session_${sessionId}_index`);
      sessionStorage.removeItem(`session_${sessionId}_results`);
      navigate(`/results/${sessionId}`);
    } catch (e) {
      console.error(e);
    }
  }

  if (!sessionData) return null;

  const tasks = sessionData.tasks;
  const currentTask = tasks[currentIndex];
  // ← синхронно оновлюємо ref — не через useEffect
  currentTaskRef.current = currentTask;

  const isLast = currentIndex === tasks.length - 1;

  async function handleSubmitAnswer() {
    if (isTimeUp) return;
    if (!answer.trim()) return;
    if (submittingRef.current) return;
    if (hasFinishedRef.current) return;

    submittingRef.current = true;
    setLoading(true);

    const timeSpent = Math.round((Date.now() - taskStartTimeRef.current) / 1000);

    try {
      const { data } = await api.post(`/sessions/${sessionId}/answer`, {
        task_id: currentTask.id,
        answer: answer.trim(),
        time_spent_seconds: timeSpent,
      });

      setResults((prev) => [...prev, data]);
      setAnswer('');

      if (isLast) {
        if (hasFinishedRef.current) return;
        hasFinishedRef.current = true;
        await api.post(`/sessions/${sessionId}/finish`);
        sessionStorage.removeItem(`session_${sessionId}_index`);
        sessionStorage.removeItem(`session_${sessionId}_results`);
        navigate(`/results/${sessionId}`);
        return;
      } else {
        setCurrentIndex(currentIndex + 1);
        const newTime = Date.now();
        setTaskStartTime(newTime);
        taskStartTimeRef.current = newTime; // ← синхронізуємо ref
      }
    } catch (err) {
      console.error(err);
      alert('Помилка відправки відповіді: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    } finally {
      setLoading(false);
      if (!hasFinishedRef.current) {
        submittingRef.current = false;
      }
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.timer}>
          ⏳ {remaining === null ? '...' : formatTime(remaining)}
        </div>
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
          disabled={isTimeUp}
          ref={inputRef}
          type="text"
          value={answer}
          onChange={(e) => {
            const value = e.target.value;
            if (currentTask.answer_type === 'number') {
              const filtered = value.replace(/[^0-9\-.,]/g, '');
              setAnswer(filtered);
            } else {
              setAnswer(value);
            }
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !loading && !isTimeUp) handleSubmitAnswer();
          }}
          className={styles.input}
          placeholder={
            currentTask.answer_type === 'number'
              ? 'Введіть число'
              : 'Введіть відповідь'
          }
          autoFocus
        />

        <button
          type="button"
          onClick={handleSubmitAnswer}
          className={styles.submitBtn}
          disabled={loading || !answer.trim() || isTimeUp}
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