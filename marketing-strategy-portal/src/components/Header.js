import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = ({ /* onToggleSidebar prop removed */ }) => {
  const [isSticky, setIsSticky] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setIsSticky(true);
        document.body.classList.add('has-sticky-header');
      } else {
        setIsSticky(false);
        document.body.classList.remove('has-sticky-header');
      }
    };

    window.addEventListener('scroll', handleScroll);
    
    // Clean up
    return () => {
      window.removeEventListener('scroll', handleScroll);
      document.body.classList.remove('has-sticky-header');
    };
  }, []);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
    // Prevent scrolling when mobile menu is open
    if (!isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
    document.body.style.overflow = 'auto';
  };

  return (
    <header className={`header ${isSticky ? 'sticky' : ''}`}>
      <div className="header-container">
        <div className="logo">
          <Link to="/" className="logo-link" onClick={closeMobileMenu}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#6366F1" />
              <path d="M2 17L12 22L22 17" stroke="#6366F1" strokeWidth="2" />
              <path d="M2 12L12 17L22 12" stroke="#6366F1" strokeWidth="2" />
            </svg>
            <span>Mark.AI</span>
          </Link>
        </div>
        
        <nav className={`navigation ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          <div className="mobile-menu-header">
            <div className="logo">
              <Link to="/" className="logo-link" onClick={closeMobileMenu}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#6366F1" />
                  <path d="M2 17L12 22L22 17" stroke="#6366F1" strokeWidth="2" />
                  <path d="M2 12L12 17L22 12" stroke="#6366F1" strokeWidth="2" />
                </svg>
                <span>Mark.AI</span>
              </Link>
            </div>
            <button className="close-menu-btn" onClick={toggleMobileMenu}>
              <span className="close-icon">×</span>
            </button>
          </div>
          
          <ul className="nav-links">
            <li className="nav-item">
              <Link to="/about" className="nav-link" onClick={closeMobileMenu}>About Us</Link>
            </li>
            <li className="nav-item">
              <Link to="/pricing" className="nav-link" onClick={closeMobileMenu}>Pricing</Link>
            </li>
            <li className="nav-item">
              <Link to="/demo" className="nav-link" onClick={closeMobileMenu}>Demo</Link>
            </li>
            <li className="nav-item">
              <Link to="/chat" className="nav-link" onClick={closeMobileMenu}>Chat with me</Link>
            </li>
            <li className="nav-item">
              <Link to="/contact" className="nav-link" onClick={closeMobileMenu}>Contact us</Link>
            </li>
          </ul>
          
          <div className="mobile-auth-buttons">
            <Link to="/login" className="login-btn" onClick={closeMobileMenu}>Login</Link>
            <Link to="/signup" className="try-free-btn" onClick={closeMobileMenu}>Try for free</Link>
          </div>
        </nav>
        
        <div className="auth-buttons desktop-only">
          <Link to="/login" className="login-btn">Login</Link>
          <Link to="/signup" className="try-free-btn">Try for free</Link>
        </div>
        
        <button className="menu-toggle" onClick={toggleMobileMenu}>
          <span className="menu-icon"></span>
          <span className="menu-icon"></span>
          <span className="menu-icon"></span>
        </button>
      </div>
      
      {isMobileMenuOpen && <div className="mobile-menu-overlay" onClick={closeMobileMenu}></div>}
    </header>
  );
};

export default Header; 