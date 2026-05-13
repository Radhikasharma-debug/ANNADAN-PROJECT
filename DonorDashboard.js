import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import './Dashboard.css';

const DonorDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDonorStats();
  }, []);

  const fetchDonorStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/donor-stats');
      
      if (response.data?.success) {
        setStats(response.data.donor_stats);
      } else {
        setError('Failed to load dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="dashboard-loading">📊 Loading your impact...</div>;
  if (error) return <div className="dashboard-error">⚠️ {error}</div>;
  if (!stats) return <div className="dashboard-empty">No data available</div>;

  return (
    <div className="donor-dashboard">
      {/* Impact Message */}
      <div className="dashboard-hero">
        <h2>🎉 Your Impact</h2>
        <p className="impact-message">{stats.impact_message}</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {/* Total Meals Saved Card */}
        <div className="stat-card primary">
          <div className="stat-icon">🍛</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.total_meals_saved}kg</h3>
            <p className="stat-label">Food Donated</p>
          </div>
        </div>

        {/* People Helped Card */}
        <div className="stat-card success">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.people_helped}</h3>
            <p className="stat-label">People Helped</p>
          </div>
        </div>

        {/* Total Donations Card */}
        <div className="stat-card info">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.total_donations}</h3>
            <p className="stat-label">Total Donations</p>
          </div>
        </div>

        {/* This Month Card */}
        <div className="stat-card warning">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.this_month_donations}</h3>
            <p className="stat-label">This Month</p>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="status-breakdown">
        <h3>📊 Donation Status</h3>
        <div className="status-grid">
          <div className="status-item available">
            <span className="status-badge">Available</span>
            <span className="status-count">{stats.status_breakdown.available}</span>
          </div>
          <div className="status-item accepted">
            <span className="status-badge">Accepted</span>
            <span className="status-count">{stats.status_breakdown.accepted}</span>
          </div>
          <div className="status-item collected">
            <span className="status-badge">Collected</span>
            <span className="status-count">{stats.status_breakdown.collected}</span>
          </div>
          <div className="status-item completed">
            <span className="status-badge">Completed</span>
            <span className="status-count">{stats.status_breakdown.completed}</span>
          </div>
        </div>
      </div>

      {/* Recent Donations */}
      {stats.recent_donations && stats.recent_donations.length > 0 && (
        <div className="recent-section">
          <h3>📝 Recent Donations</h3>
          <div className="donations-list">
            {stats.recent_donations.map((donation, idx) => (
              <div key={idx} className="donation-item">
                <div className="donation-info">
                  <h4>{donation.food_type}</h4>
                  <p className="food-details">
                    <span>📍 {donation.location?.address}</span>
                    <span>🕐 {new Date(donation.created_at).toLocaleDateString()}</span>
                  </p>
                </div>
                <div className="donation-meta">
                  <span className="quantity-badge">{donation.quantity} {donation.unit}</span>
                  <span className={`status-badge status-${donation.status}`}>
                    {donation.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Call to Action */}
      <div className="cta-section">
        <h3>Want to help more? 💪</h3>
        <button className="btn-primary" onClick={() => window.location.href = '/post-food'}>
          Post More Food →
        </button>
      </div>
    </div>
  );
};

export default DonorDashboard;
