import React, { useState } from 'react';
import './FeatureButtons.css';

const FeatureButtons = () => {
  const [activeButton, setActiveButton] = useState('Avatars');

  const buttons = [
    { id: 'Avatars', label: 'Avatars' },
    { id: 'VideoPersonalization', label: 'Video Personalization' },
    { id: 'TextToSpeech', label: 'Text to speech' },
    { id: 'Dubbing', label: 'Dubbing' },
    { id: 'Lipsync', label: 'Lipsync' }
  ];

  const handleButtonClick = (buttonId) => {
    setActiveButton(buttonId);
    // Here you could add functionality to show different content based on the active button
  };

  return (
    <div className="feature-buttons-container">
      <div className="feature-buttons">
        {buttons.map((button) => (
          <button
            key={button.id}
            className={`feature-button ${activeButton === button.id ? 'active' : ''}`}
            onClick={() => handleButtonClick(button.id)}
          >
            {button.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default FeatureButtons; 