import React, { useState } from 'react';
import Header from '../components/Header';
import './Contact.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send the form data to your server
    console.log('Form submitted:', formData);
    setSubmitted(true);
  };

  return (
    <div className="contact-screen">
      <Header />
      <main className="main-content">
        <section className="contact-section">
          <div className="contact-container">
            <h1 className="contact-title">Contact us</h1>
            
            {submitted ? (
              <div className="submission-success">
                <p className="greeting">Hello from the Contact page!</p>
                <p>Thank you for your message. We'll get back to you as soon as possible!</p>
              </div>
            ) : (
              <>
                <p className="greeting">Hello from the Contact page!</p>
                <p className="contact-subtitle">
                  Have questions or need help? We're here for you. Fill out the form below and our team will get back to you shortly.
                </p>
                
                <form className="contact-form" onSubmit={handleSubmit}>
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="name">Your Name</label>
                      <input 
                        type="text" 
                        id="name" 
                        name="name" 
                        value={formData.name}
                        onChange={handleChange}
                        required
                      />
                    </div>
                    
                    <div className="form-group">
                      <label htmlFor="email">Email Address</label>
                      <input 
                        type="email" 
                        id="email" 
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="subject">Subject</label>
                    <input 
                      type="text" 
                      id="subject" 
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="message">Message</label>
                    <textarea 
                      id="message" 
                      name="message" 
                      rows="5"
                      value={formData.message}
                      onChange={handleChange}
                      required
                    ></textarea>
                  </div>
                  
                  <button type="submit" className="submit-button">Send Message</button>
                </form>
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Contact; 