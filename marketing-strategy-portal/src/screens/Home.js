import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import TryItYourself from '../components/TryItYourself';
import FeatureButtons from '../components/FeatureButtons';
import BrandsShowcase from '../components/BrandsShowcase';
import HowItWorks from '../components/HowItWorks';
import MarketingSection from '../components/MarketingSection';
import FAQ from '../components/FAQ';
import Footer from '../components/Footer';
import MagnetLines from '../animations/MagnetLines';
import './Home.css';

const Home = () => {
  const [visibleSections, setVisibleSections] = useState({
    hero: false,
    features: false,
    tryIt: false,
    brands: false,
    howItWorks: false,
    marketing: false,
    faq: false
  });

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
    
    // Initialize section visibility
    const handleScroll = () => {
      const sections = {
        hero: document.querySelector('.hero-section'),
        features: document.querySelector('.feature-buttons-container'),
        tryIt: document.querySelector('.try-it-yourself'),
        brands: document.querySelector('.brands-showcase'),
        howItWorks: document.querySelector('.how-it-works'),
        marketing: document.querySelector('.marketing-section'),
        faq: document.querySelector('.faq-section')
      };
      
      // Update visibility state for each section
      Object.entries(sections).forEach(([key, section]) => {
        if (section) {
          const rect = section.getBoundingClientRect();
          const isVisible = (
            rect.top <= (window.innerHeight * 0.75) &&
            rect.bottom >= (window.innerHeight * 0.25)
          );
          
          setVisibleSections(prev => ({
            ...prev,
            [key]: isVisible
          }));
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check initial visibility
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="home-screen">
      <Header />
      <main className="main-content">
        <section className={`hero-section ${visibleSections.hero ? 'fade-in active' : 'fade-in'}`}>
          <div className="hero-container">
            <div className="hero-content">
              <h1 className="hero-title">Create and Personalize <br></br> Videos in Seconds</h1>
              <p className="hero-subtitle">Produce studio-quality videos in any language, without a camera or crew</p>
            </div>
            <div className="hero-animation">
              <MagnetLines 
                rows={9}
                columns={9}
                containerSize="40vmin"
                lineColor="#6366f1"
                lineWidth="0.5vmin"
                lineHeight="6vmin"
                baseAngle={-10}
                className="hero-magnet-lines"
              />
            </div>
          </div>
        </section>
        
        <div className={`section-wrapper ${visibleSections.features ? 'slide-up active' : 'slide-up'}`}>
          <FeatureButtons />
        </div>
        
        <div className={`section-wrapper ${visibleSections.tryIt ? 'slide-up active' : 'slide-up'}`}>
          <TryItYourself />
        </div>
        
        <div className={`section-wrapper ${visibleSections.brands ? 'fade-in active' : 'fade-in'}`}>
          <BrandsShowcase />
        </div>
        
        <div className={`section-wrapper ${visibleSections.howItWorks ? 'slide-up active' : 'slide-up'}`}>
          <HowItWorks />
        </div>
        
        <div className={`section-wrapper ${visibleSections.marketing ? 'fade-in active' : 'fade-in'}`}>
          <MarketingSection />
        </div>
        
        <div className={`section-wrapper ${visibleSections.faq ? 'slide-up active' : 'slide-up'}`}>
          <FAQ />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default Home; 