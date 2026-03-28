// Feature: ClutchUp Frontend Application
// Traceability: All Features

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { TournamentsPage } from './pages/TournamentsPage';
import { TeamsPage } from './pages/TeamsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <nav className="navbar">
            <h1>ClutchUp</h1>
            <div className="nav-links">
              <Link to="/">Home</Link>
              <Link to="/tournaments">Tournaments</Link>
              <Link to="/teams">Teams</Link>
            </div>
          </nav>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/tournaments" element={<TournamentsPage />} />
              <Route path="/teams" element={<TeamsPage />} />
            </Routes>
          </main>
        </div>
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
