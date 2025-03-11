import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './Pricing.css';

const Pricing = () => {
  const [billingCycle, setBillingCycle] = useState('yearly');

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for individuals and small teams',
      monthlyPrice: 29,
      yearlyPrice: 19,
      features: [
        'Up to 5 users',
        '50 AI video generations/month',
        'Basic editing tools',
        '720p video quality',
        'Email support'
      ],
      buttonText: 'Start free trial',
      popular: false
    },
    {
      name: 'Professional',
      description: 'For growing businesses and marketing teams',
      monthlyPrice: 79,
      yearlyPrice: 59,
      features: [
        'Up to 15 users',
        '200 AI video generations/month',
        'Advanced editing tools',
        '1080p video quality',
        'Priority email & chat support',
        'Custom branding options',
        'Analytics dashboard'
      ],
      buttonText: 'Start free trial',
      popular: true
    },
    {
      name: 'Enterprise',
      description: 'For large organizations with complex needs',
      monthlyPrice: 199,
      yearlyPrice: 149,
      features: [
        'Unlimited users',
        'Unlimited AI video generations',
        'Full suite of editing tools',
        '4K video quality',
        '24/7 dedicated support',
        'Advanced customization',
        'Comprehensive analytics',
        'API access',
        'SSO & advanced security'
      ],
      buttonText: 'Contact sales',
      popular: false
    }
  ];

  return (
    <div className="pricing-screen">
      <Header />
      
      <main className="pricing-main">
        <div className="pricing-hero">
          <div className="pricing-hero-content">
            <h1 className="pricing-title" data-aos="fade-up" data-aos-duration="1000">
              Simple, transparent pricing
            </h1>
            <p className="pricing-subtitle" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="100">
              Choose the perfect plan for your marketing needs
            </p>
            
            <div className="billing-toggle" data-aos="fade-up" data-aos-duration="1000" data-aos-delay="200">
              <span className={`toggle-option ${billingCycle === 'monthly' ? 'active' : ''}`}>
                Monthly
              </span>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={billingCycle === 'yearly'}
                  onChange={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                />
                <span className="slider"></span>
              </label>
              <span className={`toggle-option ${billingCycle === 'yearly' ? 'active' : ''}`}>
                Yearly
                <span className="discount-badge">Save 25%</span>
              </span>
            </div>
          </div>
        </div>
        
        <div className="pricing-plans-container">
          <div className="pricing-plans">
            {plans.map((plan, index) => (
              <div 
                className={`pricing-plan ${plan.popular ? 'popular' : ''}`}
                key={index}
                data-aos="fade-up"
                data-aos-duration="1000"
                data-aos-delay={150 * (index + 1)}
              >
                {plan.popular && <div className="popular-badge">Most Popular</div>}
                
                <h2 className="plan-name">{plan.name}</h2>
                <p className="plan-description">{plan.description}</p>
                
                <div className="plan-price">
                  <span className="currency">$</span>
                  <span className="amount">
                    {billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice}
                  </span>
                  <span className="period">/ month</span>
                </div>
                
                {billingCycle === 'yearly' && (
                  <div className="yearly-savings">
                    ${(plan.monthlyPrice - plan.yearlyPrice) * 12} yearly savings
                  </div>
                )}
                
                <ul className="plan-features">
                  {plan.features.map((feature, i) => (
                    <li key={i}>
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
                
                <button className={`plan-button ${plan.popular ? 'primary' : 'secondary'}`}>
                  {plan.buttonText}
                </button>
              </div>
            ))}
          </div>
        </div>
        
        <div className="pricing-faq" data-aos="fade-up" data-aos-duration="1000">
          <h2 className="faq-title">Frequently Asked Questions</h2>
          
          <div className="faq-grid">
            <div className="faq-item">
              <h3 className="faq-question">Can I upgrade or downgrade my plan later?</h3>
              <p className="faq-answer">
                Yes, you can upgrade or downgrade your plan at any time. Changes to a higher-tier plan will take effect immediately. Downgrades will take effect at the end of your current billing cycle.
              </p>
            </div>
            
            <div className="faq-item">
              <h3 className="faq-question">Do you offer discounts for non-profits or educational institutions?</h3>
              <p className="faq-answer">
                Yes, we offer special pricing for eligible non-profit organizations and educational institutions. Please contact our sales team for more information.
              </p>
            </div>
            
            <div className="faq-item">
              <h3 className="faq-question">What happens if I exceed my monthly video generation limit?</h3>
              <p className="faq-answer">
                If you reach your monthly limit, you can purchase additional video generations as needed or upgrade to a higher tier plan. We'll notify you when you're approaching your limit.
              </p>
            </div>
            
            <div className="faq-item">
              <h3 className="faq-question">Is there a free trial available?</h3>
              <p className="faq-answer">
                Yes, all plans come with a 14-day free trial so you can test the platform before committing. No credit card required to start your trial.
              </p>
            </div>
            
            <div className="faq-item">
              <h3 className="faq-question">How does billing work?</h3>
              <p className="faq-answer">
                You'll be billed at the start of each billing cycle (monthly or yearly, depending on your preference). We accept all major credit cards and PayPal.
              </p>
            </div>
            
            <div className="faq-item">
              <h3 className="faq-question">Do you offer custom enterprise solutions?</h3>
              <p className="faq-answer">
                Absolutely. Our enterprise plan can be customized to meet your specific requirements. Contact our sales team to discuss your needs and get a tailored solution.
              </p>
            </div>
          </div>
        </div>
        
        <div className="pricing-cta" data-aos="fade-up" data-aos-duration="1000">
          <div className="cta-content">
            <h2 className="cta-title">Ready to transform your marketing?</h2>
            <p className="cta-description">Join thousands of marketers using our platform to create engaging video content at scale.</p>
            <div className="cta-buttons">
              <button className="cta-button primary">Start free trial</button>
              <button className="cta-button secondary">Contact sales</button>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Pricing; 