import React, { createContext, useState, useContext, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark');
  const [accentColor, setAccentColor] = useState('blue');

  useEffect(() => {
    // Get theme from localStorage or system preference
    const savedTheme = localStorage.getItem('theme');
    const savedAccentColor = localStorage.getItem('accentColor');
    
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      setTheme('light');
    }
    
    if (savedAccentColor) {
      setAccentColor(savedAccentColor);
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    
    // Apply accent color
    root.style.setProperty('--accent-color', getAccentColorValue(accentColor));
    
    // Save to localStorage
    localStorage.setItem('theme', theme);
    localStorage.setItem('accentColor', accentColor);
  }, [theme, accentColor]);

  const getAccentColorValue = (color) => {
    const colors = {
      blue: '#3b82f6',
      purple: '#8b5cf6',
      pink: '#ec4899',
      green: '#10b981',
      orange: '#f59e0b',
      red: '#ef4444',
      indigo: '#6366f1',
      teal: '#14b8a6',
    };
    return colors[color] || colors.blue;
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const changeAccentColor = (color) => {
    setAccentColor(color);
  };

  const value = {
    theme,
    accentColor,
    toggleTheme,
    changeAccentColor,
    isDark: theme === 'dark',
    isLight: theme === 'light',
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};