import React, { useState, useEffect, Suspense } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Context
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

// Components
import Navbar from './components/Navbar/Navbar';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import ScrollToTop from './components/UI/ScrollToTop';
import CursorFollower from './components/UI/CursorFollower';
import ParticleBackground from './components/UI/ParticleBackground';

// Pages (Lazy loaded for performance)
const Home = React.lazy(() => import('./pages/Home/Home'));
const Destinations = React.lazy(() => import('./pages/Destinations/Destinations'));
const DestinationDetail = React.lazy(() => import('./pages/Destinations/DestinationDetail'));
const Bookings = React.lazy(() => import('./pages/Bookings/Bookings'));
const Profile = React.lazy(() => import('./pages/Profile/Profile'));
const Login = React.lazy(() => import('./pages/Auth/Login'));
const Register = React.lazy(() => import('./pages/Auth/Register'));
const AIAssistant = React.lazy(() => import('./pages/AIAssistant/AIAssistant'));
const VirtualTours = React.lazy(() => import('./pages/VirtualTours/VirtualTours'));
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
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Simulate initial loading - reduced for debugging
    const timer = setTimeout(() => {
      setLoading(false);
      setMounted(true);
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
            {/* Particle Background */}
            <ParticleBackground />
            
            {/* Cursor Follower */}
            <CursorFollower />
            
            {/* Navigation */}
            <Navbar />
            
            {/* Main Content */}
            <main className="relative z-10">
              <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial="initial"
                  animate="in"
                  exit="out"
                  variants={pageVariants}
                  transition={pageTransition}
                >
                  <Suspense fallback={
                    <div className="min-h-screen flex items-center justify-center">
                      <LoadingSpinner size="medium" text="Loading page..." />
                    </div>
                  }>
                    <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/destinations" element={<Destinations />} />
                      <Route path="/destinations/:id" element={<DestinationDetail />} />
                      <Route path="/bookings" element={<Bookings />} />
                      <Route path="/profile" element={<Profile />} />
                      <Route path="/login" element={<Login />} />
                      <Route path="/register" element={<Register />} />
                      <Route path="/ai-assistant" element={<AIAssistant />} />
                      <Route path="/virtual-tours" element={<VirtualTours />} />
                      <Route path="/about" element={<About />} />
                      <Route path="/contact" element={<Contact />} />
                    </Routes>
                  </Suspense>
                </motion.div>
              </AnimatePresence>
            </main>
            
            {/* Scroll to Top Button */}
            <ScrollToTop />
            
            {/* Toast Notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#f8fafc',
                  backdropFilter: 'blur(10px)',
                  fontSize: '14px',
                  borderRadius: '12px',
                  padding: '16px',
                  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                },
                success: {
                  iconTheme: {
                    primary: '#00ff88',
                    secondary: '#0a0a0a',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ff006e',
                    secondary: '#0a0a0a',
                  },
                },
              }}
            />
          </div>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;