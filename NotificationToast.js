import React, { useEffect, useState } from 'react';
import { FaTimes, FaCheckCircle, FaExclamationCircle, FaInfoCircle } from 'react-icons/fa';
import '../styles/NotificationToast.css';

const NotificationToast = ({ 
  id, 
  type = 'info', 
  title, 
  message, 
  icon,
  autoCloseDuration = 5000,
  onClose 
}) => {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (autoCloseDuration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoCloseDuration);

      return () => clearTimeout(timer);
    }
  }, [autoCloseDuration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      onClose?.(id);
    }, 300);
  };

  const getIcon = () => {
    if (icon) return icon;
    
    switch (type) {
      case 'success':
        return <FaCheckCircle />;
      case 'error':
        return <FaExclamationCircle />;
      case 'info':
        return <FaInfoCircle />;
      default:
        return <FaInfoCircle />;
    }
  };

  return (
    <div 
      className={`notification-toast ${type} ${isExiting ? 'exit' : 'enter'}`}
      role="alert"
    >
      <div className="toast-icon">
        {getIcon()}
      </div>
      
      <div className="toast-content">
        {title && <div className="toast-title">{title}</div>}
        {message && <div className="toast-message">{message}</div>}
      </div>

      <button
        className="toast-close-button"
        onClick={handleClose}
        aria-label="Close notification"
      >
        <FaTimes />
      </button>

      <div className="toast-progress-bar"></div>
    </div>
  );
};

export default NotificationToast;
