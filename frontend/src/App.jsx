import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Session } from './pages/Session';
import { Results } from './pages/Results';
import { Profile } from './pages/Profile';
import { Diagnostic } from './pages/Diagnostic';
import { Guest } from './pages/Guest';
import { TeacherDashboard } from './pages/TeacherDashboard';
import { DbAdminDashboard } from './pages/DbAdminDashboard';
import { SystemAdminDashboard } from './pages/SystemAdminDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/diagnostic" element={<Diagnostic />} />
        <Route path="/guest" element={<Guest />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/session/:sessionId" element={<Session />} />
        <Route path="/results/:sessionId" element={<Results />} />
        <Route path="/teacher" element={<TeacherDashboard />} />
        <Route path="/admin/db" element={<DbAdminDashboard />} />
        <Route path="/admin/users" element={<SystemAdminDashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;