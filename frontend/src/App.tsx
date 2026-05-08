// Feature: ClutchUp Frontend Application
// Traceability: All Features

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { TournamentsPage } from './pages/TournamentsPage';
import { TournamentCreatePage } from './pages/TournamentCreatePage';
import { TournamentDetailPage } from './pages/TournamentDetailPage';
import { TournamentEditPage } from './pages/TournamentEditPage';
import { TeamsPage } from './pages/TeamsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function NavBar() {
  const { currentPlayer, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <h1>ClutchUp</h1>
      <div className="nav-links">
        <Link to="/">Home</Link>
        {isAuthenticated ? (
          <>
            <Link to="/tournaments">Tournaments</Link>
            <Link to="/tournaments/create">Create Tournament</Link>
            <Link to="/teams">Teams</Link>
            <Link to="/profile">Profile</Link>
            <span style={{ marginLeft: 12 }}>👤 {currentPlayer?.username}</span>
            <button onClick={handleLogout} style={{ marginLeft: 8 }}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Sign In</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <div className="app">
            <NavBar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/tournaments" element={<ProtectedRoute><TournamentsPage /></ProtectedRoute>} />
                <Route path="/tournaments/create" element={<ProtectedRoute><TournamentCreatePage /></ProtectedRoute>} />
                <Route path="/tournaments/:id" element={<ProtectedRoute><TournamentDetailPage /></ProtectedRoute>} />
                <Route path="/tournaments/:id/edit" element={<ProtectedRoute><TournamentEditPage /></ProtectedRoute>} />
                <Route path="/teams" element={<ProtectedRoute><TeamsPage /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              </Routes>
            </main>
          </div>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

const HomePage = () => (
  <div className="home-page">
    <h1>Welcome to ClutchUp</h1>
    <p>A beginner-friendly competitive gaming platform</p>
    <div className="features">
      <div className="feature">
        <h3>Rank-Based Tournaments</h3>
        <p>Compete with players at your skill level</p>
      </div>
      <div className="feature">
        <h3>Team Play</h3>
        <p>Create teams and compete together</p>
      </div>
      <div className="feature">
        <h3>Progression & Badges</h3>
        <p>Earn rewards and track your progress</p>
      </div>
    </div>
  </div>
);

export default App;
