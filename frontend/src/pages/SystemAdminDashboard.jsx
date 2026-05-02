import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import styles from './SystemAdminDashboard.module.css';

const ROLE_LABEL = {
  student: 'студент',
  teacher: 'викладач',
  db_admin: 'адмін БД',
  system_admin: 'адмін сервісу',
};

export function SystemAdminDashboard() {
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [users, setUsers] = useState([]);
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
    if (user) loadUsers();
  }, [user]);

  function loadUsers() {
    setLoading(true);
    api.get('/admin/users')
      .then(({ data }) => setUsers(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  async function handleBlock(userId) {
    if (!confirm('Заблокувати цього користувача?')) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      loadUsers();
    } catch (err) {
      alert('Помилка: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    }
  }

  async function handleUnblock(userId) {
    try {
      await api.patch(`/admin/users/${userId}`, { is_active: true });
      loadUsers();
    } catch (err) {
      alert('Помилка: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    }
  }

  async function handleChangeRole(userId, newRole) {
    try {
      await api.patch(`/admin/users/${userId}`, { role: newRole });
      loadUsers();
    } catch (err) {
      alert('Помилка: ' + (err.response?.data?.detail ?? 'спробуй ще раз'));
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (!user || loading) return <div className={styles.loading}>Завантаження...</div>;

  const activeCount = users.filter((u) => u.is_active).length;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Адміністрування сервісу</h1>
          <p className={styles.subtitle}>{user.email}</p>
        </div>
        <button onClick={handleLogout} className={styles.logoutBtn}>Вийти</button>
      </header>

      <section className={styles.card}>
        <div className={styles.cardHead}>
          <h2 className={styles.cardTitle}>
            Користувачі ({activeCount} активних / {users.length} всього)
          </h2>
          <button onClick={() => setShowForm(!showForm)} className={styles.addBtn}>
            {showForm ? 'Сховати форму' : '+ Створити користувача'}
          </button>
        </div>

        {showForm && (
          <UserForm
            onCreated={() => {
              setShowForm(false);
              loadUsers();
            }}
          />
        )}

        <div className={styles.userList}>
          {users.map((u) => (
            <div key={u.id} className={`${styles.userRow} ${!u.is_active ? styles.blocked : ''}`}>
              <div className={styles.avatar}>
                {(u.full_name || u.email).charAt(0).toUpperCase()}
              </div>
              <div className={styles.userMain}>
                <div className={styles.userName}>
                  {u.full_name || 'Без імені'}
                  {!u.is_active && <span className={styles.blockedBadge}>заблоковано</span>}
                </div>
                <div className={styles.userEmail}>{u.email}</div>
              </div>
              <select
                value={u.role}
                onChange={(e) => handleChangeRole(u.id, e.target.value)}
                disabled={u.id === user.id}
                className={`${styles.roleSelect} ${styles[`role_${u.role}`]}`}
              >
                {Object.entries(ROLE_LABEL).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
              {u.is_active ? (
                <button
                  onClick={() => handleBlock(u.id)}
                  disabled={u.id === user.id}
                  className={styles.blockBtn}
                >
                  Заблокувати
                </button>
              ) : (
                <button
                  onClick={() => handleUnblock(u.id)}
                  className={styles.unblockBtn}
                >
                  Розблокувати
                </button>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function UserForm({ onCreated }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('student');
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await api.post('/admin/users', {
        email,
        password,
        full_name: fullName || null,
        role,
      });
      setEmail('');
      setPassword('');
      setFullName('');
      onCreated();
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Помилка');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.formRow}>
        <label className={styles.label}>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={styles.input}
            placeholder="user@test.com"
          />
        </label>
        <label className={styles.label}>
          Імʼя
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className={styles.input}
            placeholder="Ім'я"
          />
        </label>
      </div>
      <div className={styles.formRow}>
        <label className={styles.label}>
          Пароль
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className={styles.input}
          />
        </label>
        <label className={styles.label}>
          Роль
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className={styles.input}
          >
            {Object.entries(ROLE_LABEL).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </label>
      </div>
      {error && <div className={styles.error}>{error}</div>}
      <button type="submit" className={styles.saveBtn} disabled={saving}>
        {saving ? 'Створюю...' : 'Створити користувача'}
      </button>
    </form>
  );
}