import React, { useState } from 'react';
import './TryItYourself.css';
import image from '../image/3.webp';

const TryItYourself = () => {
  const [script, setScript] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState(0);

  const avatars = [
    { id: 0, src: '/avatars/avatar1.jpg', alt: 'Female professional avatar' },
    { id: 1, src: '/avatars/avatar2.jpg', alt: 'Female with long dark hair avatar' },
    { id: 2, src: '/avatars/avatar3.jpg', alt: 'Male with beard avatar' }
  ];

  const handleScriptChange = (e) => {
    setScript(e.target.value);
  };

  const handleAvatarSelect = (id) => {
    setSelectedAvatar(id);
  };

  const getCharCount = () => {
    return `${script.length} / 500`;
  };

  return (
    <section className="try-it-yourself">
      <div className="try-it-container">
        <div className="try-it-content">
          <h2 className="try-it-title">Try it yourself</h2>
          
          <div className="try-it-form">
            <div className="form-group">
              <label htmlFor="script">Edit your script</label>
              <div className="textarea-container">
                <textarea 
                  id="script" 
                  value={script} 
                  onChange={handleScriptChange} 
                  maxLength={500}
                />
                <div className="char-count">{getCharCount()}</div>
              </div>
            </div>
            
            {/* <div className="form-group">
              <label>Select your avatar</label>
              <div className="avatars-grid">
                {avatars.map((avatar) => (
                  <div 
                    key={avatar.id}
                    className={`avatar-option ${selectedAvatar === avatar.id ? 'selected' : ''}`}
                    onClick={() => handleAvatarSelect(avatar.id)}
                  >
                    <img src={avatar.src} alt={avatar.alt} />
                    {selectedAvatar === avatar.id && <div className="selected-indicator">✓</div>}
                  </div>
                ))}
              </div>
            </div> */}
            
            <button className="continue-btn">
              Continue <span className="arrow">→</span>
            </button>
            
            <p className="disclaimer">
              Note: We review the content of every script. Any political, offensive, or criminal material will not receive approval.
            </p>
          </div>
        </div>
        
        <div className="preview-container">
          <div className="video-preview">
            {/* This would be replaced with an actual video preview component */}
            <img 
              src={image} 
              alt="Preview of selected avatar" 
              className="preview-image"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default TryItYourself; 