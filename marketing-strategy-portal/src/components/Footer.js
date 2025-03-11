import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-brand">
            <Link to="/" className="footer-logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#6366F1" />
                <path d="M2 17L12 22L22 17" stroke="#6366F1" strokeWidth="2" />
                <path d="M2 12L12 17L22 12" stroke="#6366F1" strokeWidth="2" />
              </svg>
              <span>Mark.AI</span>
            </Link>
            <p className="footer-tagline">
              Creating personalized videos with AI has never been easier
            </p>
            <div className="social-links">
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <i className="fab fa-linkedin-in"></i>
              </a>
              <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <i className="fab fa-facebook-f"></i>
              </a>
              <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <i className="fab fa-instagram"></i>
              </a>
            </div>
          </div>
          
          <div className="footer-links-container">
            <div className="footer-links">
              <h3 className="footer-heading">Product</h3>
              <ul className="links-list">
                <li><Link to="/features">Features</Link></li>
                <li><Link to="/pricing">Pricing</Link></li>
                <li><Link to="/case-studies">Case Studies</Link></li>
                <li><Link to="/testimonials">Testimonials</Link></li>
              </ul>
            </div>
            
            <div className="footer-links">
              <h3 className="footer-heading">Company</h3>
              <ul className="links-list">
                <li><Link to="/about">About Us</Link></li>
                <li><Link to="/blog">Blog</Link></li>
                <li><Link to="/careers">Careers</Link></li>
                <li><Link to="/contact">Contact</Link></li>
              </ul>
            </div>
            
            <div className="footer-links">
              <h3 className="footer-heading">Resources</h3>
              <ul className="links-list">
                <li><Link to="/help">Help Center</Link></li>
                <li><Link to="/documentation">Documentation</Link></li>
                <li><Link to="/guides">Guides</Link></li>
                <li><Link to="/webinars">Webinars</Link></li>
              </ul>
            </div>
            
            <div className="footer-links">
              <h3 className="footer-heading">Legal</h3>
              <ul className="links-list">
                <li><Link to="/privacy">Privacy Policy</Link></li>
                <li><Link to="/terms">Terms of Service</Link></li>
                <li><Link to="/security">Security</Link></li>
                <li><Link to="/compliance">Compliance</Link></li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p className="copyright">
            © {new Date().getFullYear()} Mark.AI. All rights reserved.
          </p>
          <div className="bottom-links">
            <a href="#" className="bottom-link">Sitemap</a>
            <a href="#" className="bottom-link">Cookies</a>
            <a href="#" className="bottom-link">Accessibility</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 