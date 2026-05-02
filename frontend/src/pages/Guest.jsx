import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import styles from './Guest.module.css';

export function Guest() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    api.get('/sessions/guest/sample-tasks')
      .then(({ data }) => setTasks(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const currentTask = tasks[currentIndex];
  const isLast = currentIndex === tasks.length - 1;

  function handleSubmit() {
    if (!answer.trim() || !currentTask) return;

    const isCorrect =
      answer.trim().toLowerCase() === currentTask.correct_answer.trim().toLowerCase();

    const result = {
      task_id: currentTask.id,
      content: currentTask.content,
      user_answer: answer,
      correct_answer: currentTask.correct_answer,
      is_correct: isCorrect,
    };

    setResults([...results, result]);
    setAnswer('');

    if (isLast) {
      setFinished(true);
    } else {
      setCurrentIndex(currentIndex + 1);
    }
  }

  if (loading) return <div className={styles.loading}>Завантаження демо...</div>;
  if (tasks.length === 0) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <p className={styles.empty}>Поки немає завдань для демо. Зайди пізніше.</p>
          <Link to="/login" className={styles.linkBtn}>На вхід</Link>
        </div>
      </div>
    );
  }

  if (finished) {
    const correct = results.filter((r) => r.is_correct).length;
    const accuracy = Math.round((correct / results.length) * 100);

    return (
      <div className={styles.container}>
        <div className={styles.banner}>
          Прогрес не збережено — це був демонстраційний режим. Зареєструйся, щоб система запам'ятовувала твої результати і адаптувалась під тебе.
        </div>

        <div className={styles.card}>
          <h2 className={styles.title}>Результати демо</h2>
          <div className={styles.bigStats}>
            <div className={styles.bigStat}>
              <div className={styles.bigStatVal}>{correct}/{results.length}</div>
              <div className={styles.bigStatLabel}>правильно</div>
            </div>
            <div className={styles.bigStat}>
              <div className={styles.bigStatVal}>{accuracy}%</div>
              <div className={styles.bigStatLabel}>точність</div>
            </div>
          </div>

          <div className={styles.resultsList}>
            {results.map((r, idx) => (
              <div key={idx} className={r.is_correct ? styles.rowCorrect : styles.rowIncorrect}>
                <div className={styles.rowContent}>{r.content}</div>
                <div className={styles.rowMeta}>
                  Твоя відповідь: <strong>{r.user_answer}</strong>
                  {!r.is_correct && (
                    <> · правильна: <strong>{r.correct_answer}</strong></>
                  )}
                </div>
              </div>
            ))}
          </div>

          <button onClick={() => navigate('/register')} className={styles.primaryBtn}>
            Зареєструватись і отримати справжній підбір завдань
          </button>
          <button onClick={() => navigate('/login')} className={styles.ghostBtn}>
            Увійти
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.banner}>
        Гостьовий режим: прогрес не зберігається. Це 3 пробні завдання, щоб ти зрозумів, як працює сервіс.
      </div>

      <div className={styles.progressCard}>
        <div className={styles.progressText}>Завдання {currentIndex + 1} з {tasks.length}</div>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${((currentIndex + 1) / tasks.length) * 100}%` }}
          />
        </div>
      </div>

      <div className={styles.card}>
        <h2 className={styles.taskTitle}>{currentTask.content}</h2>
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(); }}
          placeholder="Введи відповідь"
          autoFocus
          className={styles.input}
        />
        <button
          onClick={handleSubmit}
          disabled={!answer.trim()}
          className={styles.primaryBtn}
        >
          {isLast ? 'Завершити демо' : 'Далі'}
        </button>
        <Link to="/login" className={styles.exitLink}>← Вийти з демо</Link>
      </div>
    </div>
  );
}