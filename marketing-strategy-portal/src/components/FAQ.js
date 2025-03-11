import React, { useState } from 'react';
import './FAQ.css';

const FAQ = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const faqItems = [
    {
      id: 1,
      question: "How does AI voice generation work?",
      answer: "Our AI voice generation technology analyzes speech patterns, intonation, and vocal characteristics to create natural-sounding synthetic voices. It uses deep learning models trained on thousands of hours of recorded speech to create voices that sound indistinguishable from human speech."
    },
    {
      id: 2,
      question: "Can I customize the AI avatars to match my brand identity?",
      answer: "Yes, you can fully customize our AI avatars to align with your brand. From appearance and clothing to voice tone and speaking style, our platform offers extensive customization options. For enterprise clients, we also offer custom avatar creation services to create digital personas that perfectly represent your brand."
    },
    {
      id: 3,
      question: "How many languages are supported for the text-to-speech feature?",
      answer: "Our platform currently supports 23 languages for text-to-speech conversion, including English, Spanish, French, German, Mandarin, Japanese, Arabic, and more. We regularly add support for new languages and dialects, with high-quality, natural-sounding voices for each."
    },
    {
      id: 4,
      question: "What types of businesses can benefit from AI-generated marketing content?",
      answer: "Businesses of all sizes and across industries can benefit from our AI marketing tools. E-commerce businesses can create personalized product videos, educational institutions can develop engaging learning content, real estate agents can create virtual property tours, and service providers can craft personalized client messages—all without expensive production equipment."
    },
    {
      id: 5,
      question: "How secure is the platform and my uploaded content?",
      answer: "We prioritize security and privacy. All content is encrypted during transfer and storage, and we adhere to strict data protection policies. Your content is never used to train our models without explicit permission, and you maintain full ownership and control of all generated assets."
    }
  ];

  const toggleAccordion = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <section className="faq-section">
      <div className="faq-container">
        <div className="faq-header">
          <h2 className="faq-title">Frequently Asked Questions</h2>
          <p className="faq-subtitle">
            Get answers to common questions about our AI-powered video and content creation platform
          </p>
        </div>

        <div className="faq-content">
          {faqItems.map((item, index) => (
            <div 
              key={item.id} 
              className={`faq-item ${activeIndex === index ? 'active' : ''}`}
            >
              <button 
                className="faq-question"
                onClick={() => toggleAccordion(index)}
              >
                {item.question}
                <span className="faq-icon">{activeIndex === index ? '−' : '+'}</span>
              </button>
              <div className="faq-answer-container">
                <div className="faq-answer">
                  {item.answer}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="faq-cta">
          <h3>Still have questions?</h3>
          <p>Contact our support team for personalized assistance with your specific needs</p>
          <div className="cta-buttons">
            <button className="primary-cta">Contact Support</button>
            <button className="secondary-cta">Read Documentation</button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQ; 