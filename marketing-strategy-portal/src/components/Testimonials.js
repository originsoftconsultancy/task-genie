import React from 'react';
import './Testimonials.css';

const Testimonials = () => {
  const testimonials = [
    {
      id: 1,
      quote: "Mark.AI has completely transformed our marketing approach. We're now able to create personalized videos for thousands of customers in a fraction of the time it used to take.",
      author: "Sarah Johnson",
      position: "CMO, TechGrowth",
      avatar: "https://randomuser.me/api/portraits/women/32.jpg"
    },
    {
      id: 2,
      quote: "The AI video generation capabilities are incredible. We've seen a 40% increase in engagement since implementing Mark.AI in our marketing strategy.",
      author: "Michael Chen",
      position: "Digital Marketing Director, GlobalBrand",
      avatar: "https://randomuser.me/api/portraits/men/15.jpg"
    },
    {
      id: 3,
      quote: "Being able to create videos in multiple languages with perfectly synced lip movements has helped us expand into international markets with authentic, localized content.",
      author: "Elena Rodriguez",
      position: "Head of Content, MarketSphere",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg"
    }
  ];

  return (
    <section className="testimonials">
      <div className="container">
        <div className="testimonials-header">
          <h2 className="section-title" data-aos="fade-up" data-aos-duration="1000">
            What our customers are saying
          </h2>
          <p className="section-subtitle" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="100">
            See how companies are scaling their marketing with our platform
          </p>
        </div>
        
        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div 
              className="testimonial-card" 
              key={testimonial.id}
              data-aos="fade-up"
              data-aos-duration="1000"
              data-aos-delay={index * 150}
            >
              <div className="quote-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="#f3f4f6">
                  <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                </svg>
              </div>
              
              <blockquote className="testimonial-quote">
                {testimonial.quote}
              </blockquote>
              
              <div className="testimonial-author">
                <img 
                  src={testimonial.avatar} 
                  alt={`${testimonial.author} avatar`} 
                  className="author-avatar" 
                />
                <div className="author-info">
                  <h4 className="author-name">{testimonial.author}</h4>
                  <p className="author-position">{testimonial.position}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="testimonial-stats" data-aos="fade-up" data-aos-duration="1000">
          <div className="stat-item">
            <span className="stat-value">96%</span>
            <span className="stat-label">Customer Satisfaction</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">3.2M</span>
            <span className="stat-label">Minutes of Video Generated</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">68%</span>
            <span className="stat-label">Avg. Engagement Increase</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials; 