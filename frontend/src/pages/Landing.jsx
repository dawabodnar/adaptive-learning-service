import { Link } from 'react-router-dom';
import { ThemeToggle } from '../components/ThemeToggle';
import styles from './Landing.module.css';

export function Landing() {
  return (
    <div className={styles.page}>
      <div className={styles.bgBlob1} />
      <div className={styles.bgBlob2} />

      <div className={styles.logo}>
        <div className={styles.logoMark} />
        <span>Adaptive Learning</span>
      </div>

      <div className={styles.themeToggle}>
        <ThemeToggle />
      </div>

      <main className={styles.main}>
        <section className={styles.hero}>
          <h1 className={styles.heroTitle}>
            Навчання, що{' '}
            <span className={styles.gradientText}>
              підлаштовується під тебе
            </span>
          </h1>
          <p className={styles.heroSubtitle}>
            Система оцінює твій рівень знань по кожній темі та формує сесію
            із завдань саме тієї складності, що максимально просуває твоє
            навчання у межах виділеного бюджету часу.
          </p>
          <Link to="/register" className={styles.primaryBtn}>
            Почати <span className={styles.btnArrow}>→</span>
          </Link>
        </section>

        <section className={styles.cards}>
          <div className={styles.card}>
            <div className={styles.cardNumber}>01</div>
            <h3 className={styles.cardTitle}>Підбір під рівень</h3>
            <p className={styles.cardText}>
              Лише ті завдання, що максимально розрізняють і просувають твої знання.
            </p>
          </div>

          <div className={styles.card}>
            <div className={styles.cardNumber}>02</div>
            <h3 className={styles.cardTitle}>Бюджет часу</h3>
            <p className={styles.cardText}>
              Задаєш, скільки маєш часу — система обирає набір завдань під нього.
            </p>
          </div>

          <div className={styles.card}>
            <div className={styles.cardNumber}>03</div>
            <h3 className={styles.cardTitle}>Прозорий прогрес</h3>
            <p className={styles.cardText}>
              Після кожної сесії — статистика по темах і твої слабкі місця.
            </p>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <Link to="/login" className={styles.smallLink}>
          Уже є акаунт? Увійти
        </Link>
        <span className={styles.dot}>·</span>
        <Link to="/guest" className={styles.smallLink}>
          Спробувати без реєстрації
        </Link>
      </footer>
    </div>
  );
}