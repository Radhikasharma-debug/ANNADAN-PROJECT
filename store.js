import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token'),
  
  setUser: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
    set({ user, token });
  },
  
  // Update parts of the user profile locally (does not call backend)
  updateUser: (partial) => {
    const current = JSON.parse(localStorage.getItem('user') || 'null') || {};
    const updated = { ...current, ...partial };
    localStorage.setItem('user', JSON.stringify(updated));
    set({ user: updated });
  },
  
  logout: () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
}));
