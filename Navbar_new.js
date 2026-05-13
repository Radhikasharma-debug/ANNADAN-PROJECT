import React from 'react';
import { Navbar, Container, Nav, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../utils/store';
import { useTheme } from '../utils/ThemeContext';
import { FaSignOutAlt, FaHome, FaUser, FaHandHoldingHeart, FaMoon, FaSun } from 'react-icons/fa';
import './Navbar.css';

const BrandLogo = () => (
  <div className="brand-logo">
    <div className="logo-icon">
      <FaHandHoldingHeart />
    </div>
    <div className="logo-text">
      <div className="logo-main">Annadan</div>
      <div className="logo-sub">Ek Umeed</div>
    </div>
  </div>
);

export const AppNavbar = () => {
  const { user, logout } = useAuthStore();
  const { isDarkMode, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <Navbar expand="lg" className="navbar-custom sticky-top">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold">
          <BrandLogo />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto align-items-center">
            {!user ? (
              <>
                <Nav.Link as={Link} to="/login" className="nav-text me-2">
                  Login
                </Nav.Link>
                <Nav.Link as={Link} to="/register" className="nav-text">
                  Register
                </Nav.Link>
              </>
            ) : (
              <>
                <Nav.Link as={Link} to="/dashboard" className="nav-text me-2">
                  <FaHome className="me-2" /> Dashboard
                </Nav.Link>
                <Nav.Link as={Link} to="/profile" className="nav-text me-2">
                  <FaUser className="me-2" /> Profile
                </Nav.Link>
                <Button
                  variant="light"
                  size="sm"
                  onClick={handleLogout}
                  className="logout-btn me-2"
                >
                  <FaSignOutAlt className="me-2" /> Logout
                </Button>
              </>
            )}
            
            <Button
              variant="outline-light"
              size="sm"
              onClick={toggleTheme}
              className="theme-toggle-btn"
              title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
            >
              {isDarkMode ? <FaSun /> : <FaMoon />}
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
