import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './utils/store';
import AppNavbar from './components/Navbar';
import { ThemeProvider } from './utils/ThemeContext';
import { ToastProvider } from './components/ToastContainer';
import './App.css';

const Home = lazy(() => import('./pages/Home'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const PersonalDashboard = lazy(() => import('./pages/PersonalDashboard'));
const PostFood = lazy(() => import('./pages/PostFood'));
const Profile = lazy(() => import('./pages/Profile'));
const AIFeatures = lazy(() => import('./pages/AIFeatures'));

const RouteLoader = () => (
  <div className="d-flex justify-content-center align-items-center py-5">
    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
    Loading...
  </div>
);

function App() {
  const { user } = useAuthStore();

  return (
    <ToastProvider>
      <ThemeProvider>
        <Router>
          <AppNavbar />
          <Suspense fallback={<RouteLoader />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
              <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={user ? <PersonalDashboard /> : <Navigate to="/login" />} />
              <Route
                path="/post-food"
                element={user && user.user_type === 'donor' ? <PostFood /> : <Navigate to="/login" />}
              />
              <Route path="/profile" element={<Profile />} />
              <Route path="/ai-features" element={<AIFeatures />} />
            </Routes>
          </Suspense>
        </Router>
      </ThemeProvider>
    </ToastProvider>
  );
}

export default App;
