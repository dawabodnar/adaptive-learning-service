import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Session } from './pages/Session';
import { Results } from './pages/Results';
import { Profile } from './pages/Profile';
import { Diagnostic } from './pages/Diagnostic';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/session/:sessionId" element={<Session />} />
        <Route path="/results/:sessionId" element={<Results />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/diagnostic" element={<Diagnostic />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;