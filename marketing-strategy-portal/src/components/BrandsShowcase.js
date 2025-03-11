import React, { useState, useEffect, useRef } from 'react';
import './BrandsShowcase.css';

const BrandsShowcase = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [totalSlides, setTotalSlides] = useState(0);
  const [visibleBrands, setVisibleBrands] = useState(5);
  const sliderRef = useRef(null);
  
  const brands = [
    {
      name: 'IBM',
      description: 'IBM is using our platform to streamline their marketing operations across 170+ countries.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg'
    },
    {
      name: 'Microsoft',
      description: 'Microsoft teams leverage our solution to coordinate global product launches and campaigns.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg'
    },
    {
      name: 'Google',
      description: 'Google\'s marketing division uses our platform to optimize their digital campaign performance.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg'
    },
    {
      name: 'Amazon',
      description: 'Amazon integrates our solution to analyze customer data and improve their marketing strategy.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg'
    },
    {
      name: 'Meta',
      description: 'Meta relies on our platform to manage and measure cross-platform social media campaigns.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg'
    },
    {
      name: 'Apple',
      description: 'Apple uses our platform to create consistent brand messaging across their global markets.',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg'
    }
  ];

  useEffect(() => {
    const handleResize = () => {
      let count = 5; // Default on large screens
      
      if (window.innerWidth <= 1200 && window.innerWidth > 768) {
        count = 3;
      } else if (window.innerWidth <= 768 && window.innerWidth > 480) {
        count = 2;
      } else if (window.innerWidth <= 480) {
        count = 1;
      }
      
      setVisibleBrands(count);
      setTotalSlides(Math.max(0, brands.length - count));
    };
    
    handleResize(); // Initial call
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [brands.length]);
  
  const handlePrevSlide = () => {
    setCurrentSlide(prev => Math.max(0, prev - 1));
  };
  
  const handleNextSlide = () => {
    setCurrentSlide(prev => Math.min(totalSlides, prev + 1));
  };

  const handleSliderTransition = () => {
    if (sliderRef.current) {
      sliderRef.current.style.transform = `translateX(-${currentSlide * (100 / visibleBrands)}%)`;
    }
  };
  
  useEffect(() => {
    handleSliderTransition();
  }, [currentSlide, visibleBrands]);
  
  // Automatically advance slides every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (currentSlide < totalSlides) {
        setCurrentSlide(prev => prev + 1);
      } else {
        setCurrentSlide(0);
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [currentSlide, totalSlides]);

  return (
    <section className="brands-showcase" data-aos="fade-up" data-aos-duration="1000">
      <div className="container">
        <h2 className="section-title">Trusted by Industry Leaders</h2>
        <p className="section-subtitle">Join thousands of marketing teams worldwide using our platform</p>
        
        <div className="brands-grid">
          {brands.map((brand, index) => (
            <div className="brand-card" key={index}>
              <div className="brand-logo-container">
                <img src={brand.logo} alt={`${brand.name} logo`} className="brand-logo" />
                <div className="brand-overlay">
                  <span className="brand-description">{brand.description}</span>
                </div>
              </div>
              <h3 className="brand-name">{brand.name}</h3>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BrandsShowcase; 