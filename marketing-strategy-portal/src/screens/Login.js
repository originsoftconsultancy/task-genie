import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import './Auth.css';
import image from '../image/6749e3fa3e5c5a9586ad0040_cta-bg.webp'

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [focusedField, setFocusedField] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleFocus = (field) => {
    setFocusedField(field);
  };

  const handleBlur = () => {
    setFocusedField(null);
  };

  const isFieldActive = (field) => {
    return focusedField === field || formData[field].length > 0;
  };

  return (
    <div className="auth-screen">
      <Header />
      <main className="auth-main">
        <div className="auth-container">
          <div className="auth-image-container">
            <img src={image} alt="AI-powered video creation" className="auth-image" />
            <div className="image-overlay">
              <div className="overlay-content">
                <h2>Transform your marketing</h2>
                <p>Create personalized videos at scale with our AI platform</p>
              </div>
            </div>
          </div>
          
          <div className="auth-form-container">
            <div className="auth-form-wrapper">
              <h1 className="auth-title">Welcome back</h1>
              <p className="auth-subtitle">Log in to your account to continue</p>
              
              <form className="auth-form">
                <div className="form-group">
                  <div className={`form-field ${isFieldActive('email') ? 'active' : ''}`}>
                    <input 
                      type="email" 
                      id="email" 
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      onFocus={() => handleFocus('email')}
                      onBlur={handleBlur}
                      required
                    />
                    <label htmlFor="email" className="floating-label">Email</label>
                  </div>
                </div>
                
                <div className="form-group">
                  <div className={`form-field ${isFieldActive('password') ? 'active' : ''}`}>
                    <input 
                      type="password" 
                      id="password" 
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      onFocus={() => handleFocus('password')}
                      onBlur={handleBlur}
                      required
                    />
                    <label htmlFor="password" className="floating-label">Password</label>
                  </div>
                </div>
                
                <div className="form-action">
                  <div className="remember-me">
                    <input type="checkbox" id="remember" />
                    <label htmlFor="remember">Remember me</label>
                  </div>
                  <a href="#" className="forgot-password">Forgot password?</a>
                </div>
                
                <button type="submit" className="auth-button">Login</button>
              </form>
              
              <div className="social-auth">
                <p className="social-divider"><span>Or continue with</span></p>
                <div className="social-buttons">
                  <button className="social-button google">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20Z" fill="white"/>
                      <path d="M14.9 10.1C14.9 9.3 14.8 8.8 14.7 8.3H10V10.7H12.8C12.7 11.4 12.2 12.4 11.2 13.1L11.19 13.2L13.18 14.8L13.3 14.81C14.4 13.8 15 12.2 15 10.2" fill="#4285F4"/>
                      <path d="M10 15C11.7 15 13.1 14.4 14.1 13.4L12 11.7C11.5 12.1 10.8 12.3 10 12.3C8.6 12.3 7.4 11.4 7 10.1L6.89 10.11L4.81 11.8L4.8 11.9C5.8 13.8 7.8 15 10 15Z" fill="#34A853"/>
                      <path d="M7 10.1C6.9 9.6 6.8 9.1 6.8 8.5C6.8 7.9 6.9 7.4 7 6.9L7 6.75L4.9 5.05L4.8 5.1C4.3 6.1 4 7.3 4 8.5C4 9.7 4.3 10.9 4.8 11.9L7 10.1Z" fill="#FBBC05"/>
                      <path d="M10 4.7C11 4.7 11.7 5.1 12.1 5.5L13.9 3.8C13.1 3 11.7 2.5 10 2.5C7.8 2.5 5.8 3.7 4.8 5.6L7 7.4C7.4 6.1 8.6 4.7 10 4.7Z" fill="#EA4335"/>
                    </svg>
                    <span>Google</span>
                  </button>
                  <button className="social-button github">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path fillRule="evenodd" clipRule="evenodd" d="M10 0C4.477 0 0 4.477 0 10C0 14.42 2.865 18.165 6.839 19.489C7.339 19.581 7.521 19.273 7.521 19.005C7.521 18.765 7.512 18.054 7.508 17.225C4.726 17.821 4.139 15.97 4.139 15.97C3.685 14.812 3.029 14.505 3.029 14.505C2.121 13.886 3.098 13.899 3.098 13.899C4.101 13.97 4.629 14.929 4.629 14.929C5.521 16.45 6.969 16.018 7.539 15.761C7.631 15.123 7.889 14.691 8.175 14.42C5.954 14.145 3.62 13.288 3.62 9.462C3.62 8.371 4.009 7.481 4.648 6.786C4.546 6.531 4.203 5.519 4.747 4.145C4.747 4.145 5.587 3.876 7.496 5.168C8.295 4.947 9.152 4.836 10.002 4.832C10.85 4.836 11.706 4.947 12.507 5.168C14.414 3.876 15.252 4.145 15.252 4.145C15.797 5.519 15.455 6.531 15.352 6.786C15.992 7.481 16.379 8.371 16.379 9.462C16.379 13.298 14.041 14.142 11.814 14.411C12.168 14.745 12.491 15.411 12.491 16.419C12.491 17.853 12.479 18.673 12.479 19.005C12.479 19.275 12.659 19.585 13.167 19.488C17.138 18.162 20 14.419 20 10C20 4.477 15.523 0 10 0Z" fill="#1B1F23"/>
                    </svg>
                    <span>GitHub</span>
                  </button>
                </div>
              </div>
              
              <p className="auth-redirect">
                Don't have an account? <Link to="/signup">Sign up</Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login; 