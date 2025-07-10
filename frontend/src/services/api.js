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
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  getProfile: () => api.get('/api/auth/profile'),
  updateProfile: (profileData) => api.put('/api/auth/profile', profileData),

  // Destinations
  getDestinations: (params) => api.get('/api/destinations', { params }),
  getDestination: (id) => api.get(`/api/destinations/${id}`),
  createDestination: (destinationData) => api.post('/api/destinations', destinationData),

  // Bookings
  createBooking: (bookingData) => api.post('/api/bookings', bookingData),
  getUserBookings: () => api.get('/api/bookings'),
  updateBooking: (id, bookingData) => api.put(`/api/bookings/${id}`, bookingData),
  cancelBooking: (id) => api.delete(`/api/bookings/${id}`),

  // Reviews
  createReview: (reviewData) => api.post('/api/reviews', reviewData),
  getDestinationReviews: (destinationId) => api.get(`/api/reviews/${destinationId}`),
  updateReview: (id, reviewData) => api.put(`/api/reviews/${id}`, reviewData),
  deleteReview: (id) => api.delete(`/api/reviews/${id}`),

  // AI Services
  getAIRecommendations: (preferences) => api.post('/api/ai/recommendations', preferences),
  chatWithAI: (message) => api.post('/api/chat', message),

  // Health check
  healthCheck: () => api.get('/api/health'),
};

export default api;