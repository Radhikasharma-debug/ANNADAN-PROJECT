import React, { useState, useEffect } from 'react';
import { FaTimes, FaCheckCircle, FaTrash, FaClock } from 'react-icons/fa';
import '../styles/NotificationCenter.css';

const NotificationCenter = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unread

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, filter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const endpoint = filter === 'unread' ? '/api/notifications/unread' : '/api/notifications';
      
      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        
        // Update unread count
        const unread = data.notifications.filter((n) => !n.is_read).length;
        setUnreadCount(unread);
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId, event) => {
    event?.stopPropagation?.();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // Update local state
        setNotifications((prev) =>
          prev.map((n) =>
            n._id === notificationId ? { ...n, is_read: true } : n
          )
        );
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/notifications/mark-all-read', {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setNotifications((prev) =>
          prev.map((n) => ({ ...n, is_read: true }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const deleteNotification = async (notificationId, event) => {
    event?.stopPropagation?.();
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setNotifications((prev) =>
          prev.filter((n) => n._id !== notificationId)
        );
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <div className={`notification-center-overlay ${isOpen ? 'open' : ''}`}>
      <div className="notification-center-modal">
        {/* Header */}
        <div className="notification-center-header">
          <div className="header-title-section">
            <h2 className="notification-center-title">🔔 Notifications</h2>
            {unreadCount > 0 && (
              <div className="unread-indicator">{unreadCount} new</div>
            )}
          </div>
          <button
            className="close-button"
            onClick={onClose}
            aria-label="Close notifications"
          >
            <FaTimes />
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="notification-tabs">
          <button
            className={`tab-button ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`tab-button ${filter === 'unread' ? 'active' : ''}`}
            onClick={() => setFilter('unread')}
          >
            Unread ({unreadCount})
          </button>
        </div>

        {/* Action Buttons */}
        {unreadCount > 0 && (
          <div className="notification-actions">
            <button
              className="btn-mark-all-read"
              onClick={markAllAsRead}
            >
              <FaCheckCircle className="me-1" /> Mark all as read
            </button>
          </div>
        )}

        {/* Notifications List */}
        <div className="notification-list">
          {loading ? (
            <div className="notification-loading">
              <div className="spinner-small"></div>
              Loading notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="notification-empty">
              <div className="empty-icon">📭</div>
              <p>No notifications</p>
            </div>
          ) : (
            notifications.map((notif) => (
              <div
                key={notif._id}
                className={`notification-item ${!notif.is_read ? 'unread' : 'read'}`}
                onClick={() => {
                  if (!notif.is_read) {
                    markAsRead(notif._id);
                  }
                  if (notif.action_url) {
                    window.location.href = notif.action_url;
                    onClose();
                  }
                }}
              >
                <div className="notification-icon">{notif.icon}</div>
                
                <div className="notification-content">
                  <div className="notification-title-row">
                    <h4 className="notification-title">{notif.title}</h4>
                    {notif.priority === 'high' && (
                      <span className="priority-badge high">High</span>
                    )}
                  </div>
                  <p className="notification-message">{notif.message}</p>
                  <div className="notification-meta">
                    <FaClock className="time-icon" />
                    <span className="time-text">{formatTime(notif.created_at)}</span>
                  </div>
                </div>

                <div className="notification-actions-inline">
                  {!notif.is_read && (
                    <button
                      className="btn-read"
                      onClick={(e) => markAsRead(notif._id, e)}
                      title="Mark as read"
                    >
                      <FaCheckCircle />
                    </button>
                  )}
                  <button
                    className="btn-delete"
                    onClick={(e) => deleteNotification(notif._id, e)}
                    title="Delete notification"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="notification-center-footer">
          <p className="footer-text">
            Notifications help you stay updated on your donations
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;
