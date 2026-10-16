import { useState } from 'react';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage';
import './App.css';

export default function App() {
  const [view, setView] = useState<'dashboard' | 'profile'>('dashboard');

  return (
    <div className="app">
      <header className="header">
        <h1>Cobalt Lab</h1>
        <nav className="nav">
          <button
            className={view === 'dashboard' ? 'active' : ''}
            onClick={() => setView('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={view === 'profile' ? 'active' : ''}
            onClick={() => setView('profile')}
          >
            Profile
          </button>
        </nav>
      </header>
      <main className="main">
        {view === 'dashboard' ? <Dashboard /> : <ProfilePage />}
      </main>
    </div>
  );
}