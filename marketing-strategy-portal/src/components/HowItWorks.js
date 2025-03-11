import React, { useState } from 'react';
import './HowItWorks.css';

const HowItWorks = () => {
  const [expandedItem, setExpandedItem] = useState(1);

  const features = [
    {
      id: 1,
      title: 'Video personalization',
      description: 'Change spoken words in videos with AI, i.e. the moment when you said a name or the company. Generate endless versions with different names of your clients without lifting a camera'
    },
    {
      id: 2,
      title: 'AI Avatars',
      description: 'Create realistic AI avatars that can deliver your personalized message in multiple languages and styles'
    },
    {
      id: 3,
      title: 'Text to speech',
      description: 'Convert your written text into natural-sounding speech with our advanced AI voices'
    },
    {
      id: 4,
      title: 'Video translation',
      description: 'Translate your videos into multiple languages while maintaining lip sync and natural delivery'
    },
    {
      id: 5,
      title: 'Screen recorder',
      description: 'Record your screen with audio and add professional editing touches automatically'
    }
  ];

  const toggleAccordion = (id) => {
    setExpandedItem(expandedItem === id ? null : id);
  };

  return (
    <section className="how-it-works">
      <div className="hiw-container">
        <div className="hiw-header">
          <h2 className="hiw-title">How it works?</h2>

        </div>
        
        <div className="hiw-content">
          <div className="hiw-accordion">
            {features.map((feature) => (
              <div 
                key={feature.id} 
                className={`accordion-item ${expandedItem === feature.id ? 'expanded' : ''}`}
                onClick={() => toggleAccordion(feature.id)}
              >
                <div className="accordion-header">
                  <span className="item-number">{feature.id}</span>
                  <h3 className="item-title">{feature.title}</h3>
                  <span className="expand-icon">{expandedItem === feature.id ? '▲' : '▼'}</span>
                </div>
                <div className="accordion-content">
                  <p>{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="hiw-preview">
            <div className="phone-mockup">
              <div className="phone-screen">
                <div className="app-preview">
                  <div className="avatar-preview">
                    <img src="/images/avatar-preview.jpg" alt="Avatar preview" />
                  </div>
                  <div className="avatar-bubbles">
                    <div className="speech-bubble">
                      <span>Hey there,</span>
                      <span className="highlight">was checking out</span>
                      <span>your company website!</span>
                    </div>
                    <div className="avatar-grid">
                      {[...Array(12)].map((_, i) => (
                        <div key={i} className="avatar-option"></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks; 