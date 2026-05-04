import { useThemeStore } from '../store/themeStore';
import styles from './ThemeToggle.module.css';

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={styles.toggle}
      title={isDark ? 'Світла тема' : 'Темна тема'}
      aria-label="Перемкнути тему"
    >
      {isDark ? '☀' : '☾'}
    </button>
  );
}