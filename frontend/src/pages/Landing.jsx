import { Link } from 'react-router-dom';
import { ThemeToggle } from '../components/ThemeToggle';
import styles from './Landing.module.css';

export function Landing() {
  return (
    <div className={styles.page}>
      <div className={styles.bgBlob1} />
      <div className={styles.bgBlob2} />

      <nav className={styles.nav}>
        <div className={styles.logo}>
          <div className={styles.logoMark} />
          <span>Adaptive Learning</span>
        </div>
        <div className={styles.navActions}>
          <ThemeToggle />
          <Link to="/login" className={styles.navLink}>Увійти</Link>
          <Link to="/register" className={styles.navBtn}>
            Розпочати →
          </Link>
        </div>
      </nav>

      <section className={styles.hero}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          Бакалаврська кваліфікаційна робота · 2026
        </div>
        <h1 className={styles.heroTitle}>
          Навчання, що
          <br />
          <span className={styles.gradientText}>підлаштовується під тебе</span>
        </h1>
        <p className={styles.heroSubtitle}>
          Адаптивний підбір завдань на основі ймовірнісної моделі знань (BKT)
          та теорії відповіді на завдання (IRT). Задаєш бюджет часу — система
          формує оптимальну сесію саме під твій рівень.
        </p>
        <div className={styles.heroActions}>
          <Link to="/register" className={styles.primaryBtn}>
            Створити акаунт
            <span className={styles.btnArrow}>→</span>
          </Link>
          <Link to="/guest" className={styles.ghostBtn}>
            Демо без реєстрації
          </Link>
        </div>
        <div className={styles.statsBar}>
          <div className={styles.stat}>
            <div className={styles.statValue}>BKT + IRT</div>
            <div className={styles.statLabel}>гібридний алгоритм</div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <div className={styles.statValue}>0/1</div>
            <div className={styles.statLabel}>задача про рюкзак</div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <div className={styles.statValue}>4</div>
            <div className={styles.statLabel}>ролі користувачів</div>
          </div>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHead}>
          <div className={styles.sectionTag}>Можливості</div>
          <h2 className={styles.sectionTitle}>Що робить сервіс особливим</h2>
          <p className={styles.sectionLead}>
            Чотири ключові переваги, які відрізняють цей сервіс від інших платформ
            дистанційного навчання.
          </p>
        </div>
        <div className={styles.featureGrid}>
          <Feature
            icon="◎"
            color="purple"
            title="Адаптивний підбір"
            text="BKT відстежує знання по концептах, IRT обирає завдання, що максимально розрізняють рівень студента."
          />
          <Feature
            icon="◷"
            color="blue"
            title="Бюджет часу"
            text="Маєш 15 хвилин чи годину — система сформує оптимальну сесію через задачу про рюкзак."
          />
          <Feature
            icon="◊"
            color="green"
            title="Прозорість"
            text="Жодних чорних скриньок. Видно, як змінюється модель знань після кожної відповіді."
          />
          <Feature
            icon="✦"
            color="amber"
            title="Прогрес"
            text="Історія сесій, аналіз слабких тем, особистий профіль зі статистикою росту."
          />
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHead}>
          <div className={styles.sectionTag}>Алгоритм</div>
          <h2 className={styles.sectionTitle}>Як це працює</h2>
          <p className={styles.sectionLead}>
            Три кроки повного циклу навчання — від реєстрації до аналізу результатів.
          </p>
        </div>
        <div className={styles.stepsTimeline}>
          <Step
            n="01"
            title="Реєстрація і діагностика"
            text="Створюєш акаунт або входиш через Google. Опціонально — короткий тест для початкового рівня."
          />
          <div className={styles.stepConnector} />
          <Step
            n="02"
            title="Старт сесії"
            text="Задаєш бюджет часу. Алгоритм формує оптимальний набір завдань під твій рівень знань."
          />
          <div className={styles.stepConnector} />
          <Step
            n="03"
            title="Розв'язання та аналіз"
            text="Виконуєш завдання, BKT-модель оновлюється. Наприкінці — статистика і слабкі теми."
          />
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHead}>
          <div className={styles.sectionTag}>Ролі</div>
          <h2 className={styles.sectionTitle}>Для кого створено</h2>
          <p className={styles.sectionLead}>
            Окремий інтерфейс для кожної ролі — від студента до адміністратора.
          </p>
        </div>
        <div className={styles.audienceGrid}>
          <Role
            title="Студент"
            color="purple"
            features={[
              'Персональні навчальні сесії',
              'Підбір під твій рівень знань',
              'Облік часу та історія сесій',
              'Гостьовий режим без реєстрації',
            ]}
            link="/register"
            linkText="Створити акаунт"
          />
          <Role
            title="Викладач"
            color="blue"
            features={[
              'Список усіх студентів зі статистикою',
              'Слабкі теми по кожному учню',
              'Прозорі дані про прогрес',
              'Кабінет з графіками успішності',
            ]}
            link="/login"
            linkText="Увійти у кабінет"
          />
          <Role
            title="Адмін"
            color="amber"
            features={[
              'Керування базою завдань',
              'Налаштування концептів і параметрів',
              'Управління користувачами',
              'Зміна ролей і блокування',
            ]}
            link="/login"
            linkText="Увійти як адмін"
          />
        </div>
      </section>

      <section className={styles.techSection}>
        <div className={styles.techHead}>
          <div className={styles.sectionTag}>Технічна реалізація</div>
          <h2 className={styles.sectionTitle}>Стек технологій</h2>
        </div>
        <div className={styles.techGrid}>
          <TechCard category="Бекенд" items={['Python 3.12', 'FastAPI', 'SQLAlchemy', 'PostgreSQL']} />
          <TechCard category="Фронтенд" items={['React 18', 'Vite', 'React Router', 'Zustand']} />
          <TechCard category="Алгоритми" items={['NumPy', 'BKT', 'IRT (3PL)', '0/1 Knapsack']} />
          <TechCard category="Безпека" items={['JWT (HS256)', 'bcrypt', 'OAuth 2.0', 'CORS']} />
        </div>
      </section>

      <section className={styles.cta}>
        <div className={styles.ctaCard}>
          <h2 className={styles.ctaTitle}>Готовий спробувати?</h2>
          <p className={styles.ctaText}>
            Створи акаунт за 30 секунд або одразу запусти демо без реєстрації.
            Все вже працює — просто зайди і протестуй.
          </p>
          <div className={styles.heroActions}>
            <Link to="/register" className={styles.primaryBtn}>
              Розпочати безкоштовно
              <span className={styles.btnArrow}>→</span>
            </Link>
            <Link to="/guest" className={styles.ghostBtn}>
              Демо
            </Link>
          </div>
        </div>
      </section>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div className={styles.footerLeft}>
            <div className={styles.logo}>
              <div className={styles.logoMark} />
              <span>Adaptive Learning</span>
            </div>
            <p className={styles.footerNote}>
              Програмно-апаратний сервіс дистанційного навчання
              <br />з адаптивним підбором завдань.
            </p>
          </div>
          <div className={styles.footerRight}>
            Бакалаврська кваліфікаційна робота · 2026
          </div>
        </div>
      </footer>
    </div>
  );
}

function Feature({ icon, color, title, text }) {
  return (
    <div className={`${styles.feature} ${styles[`feature_${color}`]}`}>
      <div className={styles.featureIcon}>{icon}</div>
      <h3 className={styles.featureTitle}>{title}</h3>
      <p className={styles.featureText}>{text}</p>
    </div>
  );
}

function Step({ n, title, text }) {
  return (
    <div className={styles.step}>
      <div className={styles.stepNum}>{n}</div>
      <h3 className={styles.stepTitle}>{title}</h3>
      <p className={styles.stepText}>{text}</p>
    </div>
  );
}

function Role({ title, color, features, link, linkText }) {
  return (
    <div className={`${styles.audienceCard} ${styles[`audience_${color}`]}`}>
      <h3 className={styles.audienceTitle}>{title}</h3>
      <ul className={styles.list}>
        {features.map((f, i) => (
          <li key={i}>{f}</li>
        ))}
      </ul>
      <Link to={link} className={styles.cardLink}>
        {linkText} <span className={styles.btnArrow}>→</span>
      </Link>
    </div>
  );
}

function TechCard({ category, items }) {
  return (
    <div className={styles.techCard}>
      <div className={styles.techCategory}>{category}</div>
      <div className={styles.techItems}>
        {items.map((item, i) => (
          <span key={i} className={styles.techItem}>{item}</span>
        ))}
      </div>
    </div>
  );
}