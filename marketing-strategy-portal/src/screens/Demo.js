import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Hero from '../components/Hero';
import FeatureShowcase from '../components/FeatureShowcase';
import BrandsShowcase from '../components/BrandsShowcase';
import Testimonials from '../components/Testimonials';
import CTASection from '../components/CTASection';
import './Demo.css';

const Demo = () => {
  return (
    <div className="demo-screen">
      <Header />
      
      <div className="demo-intro">
        <div className="demo-intro-content">
          <h1 className="demo-title">
            <span className="gradient-text">Interactive Showcase</span>
            <span className="demo-subtitle">Experience our platform features</span>
          </h1>
        </div>
      </div>
      
      <main className="demo-main">
        {/* <div className="section-spacing">
          <Hero />
        </div> */}
        
        <div className="section-spacing">
          <BrandsShowcase />
        </div>
        
        <div className="section-spacing">
          <FeatureShowcase />
        </div>
        
        <div className="section-spacing">
          <Testimonials />
        </div>
        
        <div className="section-spacing">
          <CTASection />
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Demo; 