import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import image1 from '../image/1.png';
import image2 from '../image/2.jpg';
import './About.css';

const About = () => {
  return (
    <div className="about-screen">
      <Header />
      <main className="main-content">
        <section className="about-hero-section">
          <div className="about-container">
            <h1 className="about-title">About Us</h1>
            {/* <div className="about-intro">
              <div className="about-intro-text">
                <p>
                  We are a passionate team dedicated to revolutionizing video personalization through AI. 
                  Our mission is to make high-quality, personalized video content accessible to businesses of all sizes.
                </p>
                <p>
                  With our cutting-edge AI-driven technology, we've helped hundreds of companies create engaging, 
                  personalized videos that resonate with their audience, driving better engagement and conversion rates.
                </p>
              </div>
              <div className="about-intro-image">
                <img src={image1} alt="AI video creation illustration" />
              </div>
            </div> */}
          </div>
        </section>
        
        <section className="about-mission-section">
          <div className="about-container">
            <div className="about-mission">
              <div className="about-mission-image">
                <img src={image2} alt="Our team working on AI technology" />
              </div>
              <div className="about-mission-text">
                <h2>Our Mission</h2>
                <p>
                  Our platform combines advanced AI models, natural language processing, and computer vision 
                  to create life-like avatars that can deliver your message in a way that feels personal and authentic.
                </p>
                <p>
                  We believe in the power of personalization to transform marketing and communication. 
                  Our goal is to empower businesses to connect with their audience on a deeper level through 
                  technology that feels human.
                </p>
                <div className="mission-stats">
                  <div className="stat-item">
                    <span className="stat-number">500+</span>
                    <span className="stat-label">Clients Worldwide</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-number">23</span>
                    <span className="stat-label">Languages Supported</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-number">1M+</span>
                    <span className="stat-label">Videos Generated</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="about-team-section">
          <div className="about-container">
            <h2 className="section-title">Our Leadership</h2>
            <div className="team-grid">
              {[1, 2, 3, 4].map((member) => (
                <div key={member} className="team-member">
                  <div className="member-photo" style={{ backgroundColor: '#f3f4f6' }}></div>
                  <h3 className="member-name">Team Member {member}</h3>
                  <p className="member-title">Co-founder & {member === 1 ? 'CEO' : member === 2 ? 'CTO' : member === 3 ? 'CMO' : 'COO'}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
        
        <section className="about-cta-section">
          <div className="about-container">
            <div className="about-cta">
              <h2>Ready to transform your video content?</h2>
              <p>Join hundreds of businesses using our AI platform to create personalized videos that connect.</p>
              <div className="cta-buttons">
                <a href="/signup" className="primary-cta">Get Started</a>
                <a href="/contact" className="secondary-cta">Contact Sales</a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default About; 