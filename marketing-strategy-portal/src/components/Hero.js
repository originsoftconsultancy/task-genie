import React from 'react';
import { Link } from 'react-router-dom';
import MagnetLines from './MagnetLines';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title" data-aos="fade-up" data-aos-duration="1000">
            Create and Personalize <br /> Videos in Seconds
          </h1>
          
          <p className="hero-subtitle" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="100">
            Produce studio-quality videos in any language, without a camera or crew
          </p>
          
          <div className="hero-cta" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
            <Link to="/signup" className="cta-button primary">
              Start for free
            </Link>
            <Link to="/demo" className="cta-button secondary">
              Request a demo
            </Link>
          </div>
          
          <div className="hero-stats" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="300">
            <div className="stat-item">
              <span className="stat-value">10M+</span>
              <span className="stat-label">Videos Generated</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-value">5K+</span>
              <span className="stat-label">Active Users</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-value">99%</span>
              <span className="stat-label">Satisfaction Rate</span>
            </div>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="animation-container">
            <MagnetLines />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero; 