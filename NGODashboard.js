import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import './Dashboard.css';

const NGODashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNGOStats();
  }, []);

  const fetchNGOStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dashboard/ngo-stats');
      
      if (response.data?.success) {
        setStats(response.data.ngo_stats);
      } else {
        setError('Failed to load dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="dashboard-loading">📊 Loading your stats...</div>;
  if (error) return <div className="dashboard-error">⚠️ {error}</div>;
  if (!stats) return <div className="dashboard-empty">No data available</div>;

  return (
    <div className="ngo-dashboard">
      {/* Impact Message */}
      <div className="dashboard-hero ngo-hero">
        <h2>🌟 {stats.ngo_name}</h2>
        <p className="impact-message">{stats.impact_message}</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {/* Food Distributed Card */}
        <div className="stat-card success">
          <div className="stat-icon">🥘</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.total_food_distributed}kg</h3>
            <p className="stat-label">Food Distributed</p>
          </div>
        </div>

        {/* People Served Card */}
        <div className="stat-card primary">
          <div className="stat-icon">👨‍👩‍👧‍👦</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.people_served}</h3>
            <p className="stat-label">People Served</p>
          </div>
        </div>

        {/* Total Pickups Card */}
        <div className="stat-card info">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.total_pickups}</h3>
            <p className="stat-label">Total Pickups</p>
          </div>
        </div>

        {/* Active Pickups Card */}
        <div className="stat-card warning">
          <div className="stat-icon">🚚</div>
          <div className="stat-content">
            <h3 className="stat-value">{stats.active_pickups}</h3>
            <p className="stat-label">Active Today</p>
          </div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="status-breakdown">
        <h3>📊 Pickup Status</h3>
        <div className="status-grid">
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

      {/* Recent Pickups */}
      {stats.recent_pickups && stats.recent_pickups.length > 0 && (
        <div className="recent-section">
          <h3>📝 Recent Pickups</h3>
          <div className="pickups-list">
            {stats.recent_pickups.map((pickup, idx) => (
              <div key={idx} className="pickup-item">
                <div className="pickup-info">
                  <h4>{pickup.food_type}</h4>
                  <p className="food-details">
                    <span>📍 {pickup.location?.address}</span>
                    <span>🕐 {new Date(pickup.created_at).toLocaleDateString()}</span>
                    <span>👤 {pickup.donor_name || 'Anonymous'}</span>
                  </p>
                </div>
                <div className="pickup-meta">
                  <span className="quantity-badge">{pickup.quantity} {pickup.unit}</span>
                  <span className={`status-badge status-${pickup.status}`}>
                    {pickup.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Call to Action */}
      <div className="cta-section">
        <h3>More food waiting! 🍽️</h3>
        <button className="btn-primary" onClick={() => window.location.href = '/find-food'}>
          Find Available Food →
        </button>
      </div>
    </div>
  );
};

export default NGODashboard;
