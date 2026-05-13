import React, { useContext, createContext, useState, useCallback } from 'react';
import NotificationToast from './NotificationToast';
import '../styles/ToastContainer.css';

// Create Toast Context
export const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

// Toast Provider Component
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((config) => {
    const id = Date.now() + Math.random();
    const toast = {
      id,
      type: config.type || 'info',
      title: config.title,
      message: config.message,
      icon: config.icon,
      autoCloseDuration: config.autoCloseDuration ?? 5000,
    };

    setToasts((prev) => [...prev, toast]);
    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const success = useCallback((title, message) => {
    return addToast({
      type: 'success',
      title,
      message,
      autoCloseDuration: 4000,
    });
  }, [addToast]);

  const error = useCallback((title, message) => {
    return addToast({
      type: 'error',
      title,
      message,
      autoCloseDuration: 5000,
    });
  }, [addToast]);

  const info = useCallback((title, message) => {
    return addToast({
      type: 'info',
      title,
      message,
      autoCloseDuration: 4000,
    });
  }, [addToast]);

  const warning = useCallback((title, message) => {
    return addToast({
      type: 'warning',
      title,
      message,
      autoCloseDuration: 4000,
    });
  }, [addToast]);

  const value = {
    addToast,
    removeToast,
    success,
    error,
    info,
    warning,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onCloseToast={removeToast} />
    </ToastContext.Provider>
  );
};

// Toast Container Component
const ToastContainer = ({ toasts, onCloseToast }) => {
  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <NotificationToast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          title={toast.title}
          message={toast.message}
          icon={toast.icon}
          autoCloseDuration={toast.autoCloseDuration}
          onClose={onCloseToast}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
