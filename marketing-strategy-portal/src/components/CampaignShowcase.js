import React, { useState } from 'react';
import './CampaignShowcase.css';

const CampaignShowcase = () => {
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  const campaigns = [
    {
      id: 1,
      name: 'Summer Collection Launch',
      type: 'Email Campaign',
      status: 'Active',
      date: 'Jun 15, 2023',
      stats: {
        sent: 15842,
        opened: 9856,
        clicked: 4321,
        converted: 1256
      },
      color: '#FEE2E2'
    },
    {
      id: 2,
      name: 'Customer Re-engagement',
      type: 'SMS Campaign',
      status: 'Scheduled',
      date: 'Jul 1, 2023',
      stats: {
        sent: 0,
        opened: 0,
        clicked: 0,
        converted: 0
      },
      color: '#E0E7FF'
    },
    {
      id: 3,
      name: 'Product Announcement',
      type: 'Social Media',
      status: 'Draft',
      date: 'Jul 10, 2023',
      stats: {
        sent: 0,
        opened: 0,
        clicked: 0,
        converted: 0
      },
      color: '#DBEAFE'
    },
    {
      id: 4,
      name: 'Holiday Special Offer',
      type: 'Email Campaign',
      status: 'Completed',
      date: 'Dec 15, 2022',
      stats: {
        sent: 25487,
        opened: 19654,
        clicked: 8769,
        converted: 3254
      },
      color: '#D1FAE5'
    },
    {
      id: 5,
      name: 'New Year Promotion',
      type: 'Email + SMS',
      status: 'Completed',
      date: 'Jan 2, 2023',
      stats: {
        sent: 35621,
        opened: 28745,
        clicked: 12587,
        converted: 5698
      },
      color: '#FEF3C7'
    }
  ];

  const handleSelectCampaign = (id) => {
    setSelectedCampaign(id === selectedCampaign ? null : id);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return '#10B981';
      case 'Scheduled':
        return '#6366F1';
      case 'Draft':
        return '#9CA3AF';
      case 'Completed':
        return '#1F2937';
      default:
        return '#9CA3AF';
    }
  };

  return (
    <div className="campaign-container">
      <div className="campaign-showcase">
        <div className="campaign-header">
          <div className="header-content">
            <h2>Your Campaigns</h2>
            <p className="header-subtitle">Manage and track performance</p>
          </div>
          <button className="new-campaign-btn">
            <span className="plus-icon">+</span>
            New Campaign
          </button>
        </div>

        <div className="campaign-list">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className={`campaign-card ${selectedCampaign === campaign.id ? 'selected' : ''}`}
              style={{ backgroundColor: campaign.color + '30' }}
              onClick={() => handleSelectCampaign(campaign.id)}
            >
              <div className="campaign-info">
                <h3 className="campaign-name">{campaign.name}</h3>
                <p className="campaign-type">{campaign.type}</p>

                <div className="campaign-meta">
                  <span 
                    className="campaign-status"
                    style={{ backgroundColor: getStatusColor(campaign.status) + '20', color: getStatusColor(campaign.status) }}
                  >
                    {campaign.status}
                  </span>
                  <span className="campaign-date">{campaign.date}</span>
                </div>
              </div>

              {selectedCampaign === campaign.id && (
                <div className="campaign-details">
                  <div className="campaign-stats">
                    <div className="stat-item">
                      <span className="stat-value">{campaign.stats.sent.toLocaleString()}</span>
                      <span className="stat-label">Sent</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{campaign.stats.opened.toLocaleString()}</span>
                      <span className="stat-label">Opened</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{campaign.stats.clicked.toLocaleString()}</span>
                      <span className="stat-label">Clicked</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{campaign.stats.converted.toLocaleString()}</span>
                      <span className="stat-label">Converted</span>
                    </div>
                  </div>

                  <div className="campaign-actions">
                    <button className="action-btn edit-btn">Edit</button>
                    <button className="action-btn duplicate-btn">Duplicate</button>
                    <button className="action-btn delete-btn">Delete</button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CampaignShowcase; 