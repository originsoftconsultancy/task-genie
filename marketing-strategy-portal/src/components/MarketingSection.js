import React, { useState } from 'react';
import './MarketingSection.css';

const MarketingSection = () => {
  const [activeTab, setActiveTab] = useState('strategy');

  const marketingContent = {
    strategy: {
      title: 'AI-Powered Marketing Strategy',
      description: 'Our AI analyzes market trends, consumer behavior, and competition to develop data-driven strategies that maximize ROI.',
      points: [
        'Competitive analysis across digital channels',
        'Consumer sentiment tracking and analysis',
        'Strategic recommendations based on market trends',
        'Performance forecasting and goal setting'
      ]
    },
    copywriting: {
      title: 'Persuasive Marketing Copy',
      description: 'Generate compelling marketing copy for any channel, tailored to your brand voice and optimized for conversion.',
      points: [
        'Email marketing campaigns with high open rates',
        'Social media content that drives engagement',
        'SEO-optimized web copy that ranks',
        'Ad copy designed to convert'
      ]
    },
    personalization: {
      title: 'Personalized Customer Journeys',
      description: 'Create personalized marketing experiences for each customer segment to improve engagement and conversion rates.',
      points: [
        'Customer segmentation based on behavior and preferences',
        'Personalized email sequences and recommendations',
        'Dynamic content adaptation',
        'Custom offers based on customer history'
      ]
    }
  };

  const selectedContent = marketingContent[activeTab];

  return (
    <section className="marketing-section">
      <div className="marketing-container">
        <div className="marketing-header">
          <h2 className="marketing-title">Text to speech that sounds human</h2>
          <p className="marketing-subtitle">
            Transform your text into natural speech across 23 languages - powered by our Myna TTS models.
          </p>
        </div>

        <div className="marketing-content">
          <div className="marketing-tabs">
            <button 
              className={`tab-button ${activeTab === 'strategy' ? 'active' : ''}`}
              onClick={() => setActiveTab('strategy')}
            >
              Marketing Strategy
            </button>
            <button 
              className={`tab-button ${activeTab === 'copywriting' ? 'active' : ''}`}
              onClick={() => setActiveTab('copywriting')}
            >
              AI Copywriting
            </button>
            <button 
              className={`tab-button ${activeTab === 'personalization' ? 'active' : ''}`}
              onClick={() => setActiveTab('personalization')}
            >
              Personalization
            </button>
          </div>

          <div className="marketing-details">
            <div className="marketing-text">
              <h3>{selectedContent.title}</h3>
              <p>{selectedContent.description}</p>
              <ul className="marketing-points">
                {selectedContent.points.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
              <button className="try-button">Generate Marketing Plan</button>
            </div>
            <div className="marketing-image">
              <div className="image-container">
                <div className="text-to-speech-demo">
                  <div className="input-area">
                    <textarea 
                      placeholder="Enter your marketing text here..." 
                      rows="4"
                      defaultValue="Our AI marketing assistant helps you create compelling campaigns that connect with your audience and drive results."
                    ></textarea>
                    <div className="text-count">120/500</div>
                  </div>
                  <div className="audio-controls">
                    <div className="voice-selector">
                      <img src="/images/ai-voice-avatar.jpg" alt="AI voice" className="voice-avatar" />
                      <span>Marketing Expert</span>
                      <span className="dropdown-icon">▼</span>
                    </div>
                    <button className="generate-button">
                      <span className="icon">🔊</span>
                      Generate Speech
                    </button>
                  </div>
                  <div className="audio-player">
                    <div className="waveform">
                      <div className="wave-bars">
                        {Array(30).fill().map((_, i) => (
                          <div key={i} className="wave-bar" style={{ height: `${Math.random() * 50 + 10}px` }}></div>
                        ))}
                      </div>
                    </div>
                    <div className="player-controls">
                      <button className="play-button">▶</button>
                      <div className="timeline">
                        <div className="progress" style={{ width: '30%' }}></div>
                      </div>
                      <span className="duration">00:32</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="marketing-cta">
          <h3>Ready to revolutionize your marketing with AI?</h3>
          <p>Join thousands of marketers using our platform to create data-driven strategies and compelling content.</p>
          <div className="cta-buttons">
            <button className="primary-cta">Start Free Trial</button>
            <button className="secondary-cta">View Case Studies</button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MarketingSection; 