import React from 'react';
import { Link } from 'react-router-dom';
import './CTASection.css';

const CTASection = () => {
  return (
    <section className="cta-section">
      <div className="cta-container">
        <div className="cta-content" data-aos="fade-up" data-aos-duration="1000">
          <h2 className="cta-title">Ready to transform your marketing?</h2>
          <p className="cta-description">
            Join thousands of marketers using our platform to create engaging video content at scale.
          </p>
          
          <div className="cta-buttons">
            <Link to="/signup" className="cta-button primary">
              Get started for free
            </Link>
            <Link to="/demo" className="cta-button secondary">
              Request a demo
            </Link>
          </div>
          
          <p className="cta-note">No credit card required. 14-day free trial.</p>
        </div>
      </div>
    </section>
  );
};

export default CTASection; 