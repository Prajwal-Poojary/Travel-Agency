import axios from 'axios';
import toast from 'react-hot-toast';

// Get backend URL from environment variables
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      
      // Only show toast if not already on login page
      if (!window.location.pathname.includes('/login')) {
        toast.error('Session expired. Please login again.');
      }
    } else if (error.response?.status === 403) {
      toast.error('Access denied. Insufficient permissions.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please check your connection.');
    } else if (!error.response) {
      toast.error('Network error. Please check your connection.');
    }
    
    return Promise.reject(error);
  }
);

// API service methods
export const apiService = {
  // Auth
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },
  getProfile: async () => {
    const response = await api.get('/api/auth/profile');
    return response.data;
  },
  updateProfile: async (profileData) => {
    const response = await api.put('/api/auth/profile', profileData);
    return response.data;
  },

  // Destinations
  getDestinations: async (params) => {
    const response = await api.get('/api/destinations', { params });
    return response.data;
  },
  getDestination: async (id) => {
    const response = await api.get(`/api/destinations/${id}`);
    return response.data;
  },
  createDestination: async (destinationData) => {
    const response = await api.post('/api/destinations', destinationData);
    return response.data;
  },
  getCountries: async () => {
    const response = await api.get('/api/destinations/countries');
    return response.data;
  },
  getActivities: async () => {
    const response = await api.get('/api/destinations/activities');
    return response.data;
  },
  getFeaturedDestinations: async () => {
    const response = await api.get('/api/destinations/featured');
    return response.data;
  },

  // Bookings
  createBooking: async (bookingData) => {
    const response = await api.post('/api/bookings', bookingData);
    return response.data;
  },
  getUserBookings: async () => {
    const response = await api.get('/api/bookings');
    return response.data;
  },
  updateBooking: async (id, bookingData) => {
    const response = await api.put(`/api/bookings/${id}`, bookingData);
    return response.data;
  },
  cancelBooking: async (id) => {
    const response = await api.delete(`/api/bookings/${id}`);
    return response.data;
  },

  // Reviews
  createReview: async (reviewData) => {
    const response = await api.post('/api/reviews', reviewData);
    return response.data;
  },
  getDestinationReviews: async (destinationId) => {
    const response = await api.get(`/api/reviews/${destinationId}`);
    return response.data;
  },
  updateReview: async (id, reviewData) => {
    const response = await api.put(`/api/reviews/${id}`, reviewData);
    return response.data;
  },
  deleteReview: async (id) => {
    const response = await api.delete(`/api/reviews/${id}`);
    return response.data;
  },

  // AI Services
  getAIRecommendations: async (preferences) => {
    const response = await api.post('/api/ai/recommendations', preferences);
    return response.data;
  },
  chatWithAI: async (message) => {
    const response = await api.post('/api/chat', message);
    return response.data;
  },

  // Virtual Tours (Mock data for now)
  getVirtualTours: async (params) => {
    // For now, return destinations as virtual tours
    const response = await api.get('/api/destinations', { params });
    return response.data;
  },
  getFeaturedVirtualTours: async (limit = 6) => {
    const response = await api.get(`/api/destinations/featured`);
    return response.data.slice(0, limit);
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;