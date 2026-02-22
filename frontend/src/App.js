import React, { useState, useEffect, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';


import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Components
import Navbar from './components/Navbar/Navbar';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Footer from './components/Footer/Footer';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import ScrollToTop from './components/UI/ScrollToTop';
import CursorFollower from './components/UI/CursorFollower';
import ParticleBackground from './components/UI/ParticleBackground';

// Pages (Lazy loaded for performance)
const Home = React.lazy(() => import('./pages/Home/Home'));
const Destinations = React.lazy(() => import('./pages/Destinations/Destinations'));
const DestinationDetail = React.lazy(() => import('./pages/Destinations/DestinationDetail'));
const Bookings = React.lazy(() => import('./pages/Bookings/EnhancedBookings'));
const Profile = React.lazy(() => import('./pages/Profile/Profile'));
const Login = React.lazy(() => import('./pages/Auth/Login'));
const Register = React.lazy(() => import('./pages/Auth/Register'));
const ForgotPassword = React.lazy(() => import('./pages/Auth/ForgotPassword'));
const ResetPassword = React.lazy(() => import('./pages/Auth/ResetPassword'));
const AIAssistant = React.lazy(() => import('./pages/AIAssistant/EnhancedAIAssistant'));
const VirtualTours = React.lazy(() => import('./pages/VirtualTours/EnhancedVirtualTours'));
const FavoritesVirtualTours = React.lazy(() => import('./pages/VirtualTours/FavoritesVirtualTours'));
const About = React.lazy(() => import('./pages/About/About'));
const Contact = React.lazy(() => import('./pages/Contact/Contact'));

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98
  },
  in: {
    opacity: 1,
    y: 0,
    scale: 1
  },
  out: {
    opacity: 0,
    y: -20,
    scale: 0.98
  }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.4
};

function App() {
  const [loading, setLoading] = useState(false); // Disable loading for debugging

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700 flex items-center justify-center">
        <LoadingSpinner size="large" text="Initializing Advanced Travel Platform..." />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <div className="App relative min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
            <ParticleBackground />
            <CursorFollower />
            <Navbar />

            <main className="relative z-10">
              <AnimatePresence mode="wait">
                <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={pageTransition}>
                  <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><LoadingSpinner size="medium" text="Loading page..." /></div>}>
                    <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/destinations" element={<ProtectedRoute><Destinations /></ProtectedRoute>} />
                      <Route path="/destinations/:id" element={<ProtectedRoute><DestinationDetail /></ProtectedRoute>} />
                      <Route path="/bookings" element={<ProtectedRoute><Bookings /></ProtectedRoute>} />
                      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                      <Route path="/login" element={<Login />} />
                      <Route path="/register" element={<Register />} />
                      <Route path="/forgot-password" element={<ForgotPassword />} />
                      <Route path="/reset-password" element={<ResetPassword />} />
                      <Route path="/ai-assistant" element={<ProtectedRoute><AIAssistant /></ProtectedRoute>} />
                      <Route path="/virtual-tours" element={<ProtectedRoute><VirtualTours /></ProtectedRoute>} />
                      <Route path="/virtual-tours/favorites" element={<ProtectedRoute><FavoritesVirtualTours /></ProtectedRoute>} />
                      <Route path="/about" element={<About />} />
                      <Route path="/contact" element={<Contact />} />
                    </Routes>
                  </Suspense>
                </motion.div>
              </AnimatePresence>
            </main>

            <ScrollToTop />
            <Footer />
            <Toaster position="top-right" toastOptions={{ duration: 4000, style: { background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)', color: '#f8fafc', backdropFilter: 'blur(10px)', fontSize: '14px', borderRadius: '12px', padding: '16px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }, }} />
          </div>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;