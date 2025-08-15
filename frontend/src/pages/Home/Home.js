import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Star, 
  Calendar, 
  Users, 
  Camera, 
  Bot, 
  Sparkles,
  ArrowRight,
  Globe,
  Zap,
  Shield,
  Award,
  TrendingUp,
  Heart,
  Lock
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useQuery } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const Home = () => {
  const { isAuthenticated } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(0);
  
  // Fetch featured destinations
  const { data: destinations, isLoading } = useQuery(
    'featured-destinations',
    () => apiService.getDestinations({ limit: 6 }),
    {
      onError: (error) => {
        console.error('Error fetching destinations:', error);
      },
      staleTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  // Hero images
  const heroImages = [
    {
      url: 'https://images.unsplash.com/photo-1512100356356-de1b84283e18?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMTM5NjQ1fDA&ixlib=rb-4.1.0&q=85',
      title: 'Luxury Seaplane Adventures',
      subtitle: 'Experience premium travel with breathtaking aerial views'
    },
    {
      url: 'https://images.unsplash.com/photo-1551918120-9739cb430c6d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxsdXh1cnklMjB0cmF2ZWx8ZW58MHx8fHwxNzUyMTM5NjQ1fDA&ixlib=rb-4.1.0&q=85',
      title: 'Infinity Pool Escapes',
      subtitle: 'Relax in luxury with stunning tropical panoramas'
    },
    {
      url: 'https://images.unsplash.com/photo-1486912500284-6f2462ba07ea?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxiZWF1dGlmdWwlMjBsYW5kc2NhcGVzfGVufDB8fHx8MTc1MjEzOTY1MHww&ixlib=rb-4.1.0&q=85',
      title: 'Mountain Sunset Retreats',
      subtitle: "Witness nature's most spectacular moments"
    }
  ];

  // Auto-rotate hero images
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroImages.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [heroImages.length]);

  // Features data
  const features = [
    {
      icon: Bot,
      title: 'AI Travel Assistant',
      description: 'Get personalized recommendations powered by advanced AI',
      gradient: 'from-blue-500 to-purple-600'
    },
    {
      icon: Camera,
      title: 'Virtual Tours',
      description: 'Explore destinations in immersive 360° experiences',
      gradient: 'from-pink-500 to-rose-600'
    },
    {
      icon: Zap,
      title: 'Real-time Booking',
      description: 'Instant reservations with live availability updates',
      gradient: 'from-green-500 to-emerald-600'
    },
    {
      icon: Shield,
      title: 'Secure Payments',
      description: 'Advanced encryption for safe transactions',
      gradient: 'from-orange-500 to-red-600'
    },
    {
      icon: Globe,
      title: 'Global Coverage',
      description: 'Discover amazing destinations worldwide',
      gradient: 'from-purple-500 to-indigo-600'
    },
    {
      icon: Award,
      title: 'Premium Experience',
      description: 'Luxury travel with exceptional service',
      gradient: 'from-yellow-500 to-orange-600'
    }
  ];

  // Statistics
  const stats = [
    { number: '50K+', label: 'Happy Travelers', icon: Users },
    { number: '200+', label: 'Destinations', icon: MapPin },
    { number: '4.9', label: 'Average Rating', icon: Star },
    { number: '24/7', label: 'Support', icon: Heart }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-screen overflow-hidden">
        {/* Background Images */}
        <div className="absolute inset-0">
          {heroImages.map((image, index) => (
            <motion.div
              key={index}
              className="absolute inset-0 bg-cover bg-center"
              style={{ backgroundImage: `url(${image.url})` }}
              initial={{ opacity: 0, scale: 1.1 }}
              animate={{ 
                opacity: index === currentSlide ? 1 : 0,
                scale: index === currentSlide ? 1 : 1.1
              }}
              transition={{ duration: 1 }}
            />
          ))}
          
          {/* Overlay */}
          <div className="absolute inset-0 bg-black/50" />
          
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary-900/30 via-transparent to-secondary-900/30" />
        </div>

        {/* Content */}
        <div className="relative z-10 h-full flex items-center justify-center px-4">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-5xl md:text-7xl font-bold mb-6">
                <span className="text-gradient">Advanced</span>
                <br />
                <span className="text-white">Travel Platform</span>
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-2xl mx-auto">
                Experience the future of travel with AI-powered recommendations, 
                virtual tours, and seamless booking
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/destinations"
                      className="btn-gradient px-8 py-4 rounded-full text-lg font-semibold hover:shadow-glow transition-all duration-300 flex items-center justify-center gap-2"
                    >
                      <Sparkles className="w-5 h-5" />
                      Explore Destinations
                    </Link>
                    
                    <Link
                      to="/ai-assistant"
                      className="glass px-8 py-4 rounded-full text-lg font-semibold hover:bg-white/20 transition-all duration-300 flex items-center justify-center gap-2"
                    >
                      <Bot className="w-5 h-5" />
                      AI Assistant
                    </Link>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="btn-gradient px-8 py-4 rounded-full text-lg font-semibold hover:shadow-glow transition-all duration-300 flex items-center justify-center gap-2"
                    >
                      <Sparkles className="w-5 h-5" />
                      Login to Explore
                    </Link>
                    <Link
                      to="/register"
                      className="glass px-8 py-4 rounded-full text-lg font-semibold hover:bg-white/20 transition-all duration-300 flex items-center justify-center gap-2"
                    >
                      <Users className="w-5 h-5" />
                      Create Account
                    </Link>
                  </>
                )}
              </div>
            </motion.div>
          </div>
        </div>

        {/* Slide Indicators */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex space-x-2">
          {heroImages.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                index === currentSlide ? 'bg-white' : 'bg-white/50'
              }`}
            />
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gradient">
              Revolutionary Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Discover the cutting-edge technology that makes your travel experience extraordinary
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="glass rounded-2xl p-6 hover:shadow-glow transition-all duration-300 group"
                >
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary-900/20 to-secondary-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-300">
                    {stat.label}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Featured Destinations (Locked until login) */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gradient">
              Featured Destinations
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              {isAuthenticated ? 'Discover our handpicked selection of the world\'s most stunning destinations' : 'Login to unlock curated destination lists tailored for you'}
            </p>
          </motion.div>

          {isAuthenticated ? (
            isLoading ? (
              <div className="flex justify-center">
                <LoadingSpinner size="large" text="Loading destinations..." />
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {destinations?.slice(0, 6)?.map((destination, index) => (
                  <motion.div
                    key={destination.destination_id}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className="glass rounded-2xl overflow-hidden hover:shadow-glow transition-all duration-300 group"
                  >
                    <div className="relative h-48 overflow-hidden">
                      <img
                        src={destination.images?.[0] || '/api/placeholder/400/300'}
                        alt={destination.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-full px-2 py-1 flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        <span className="text-white text-sm">{destination.rating}</span>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <h3 className="text-xl font-semibold text-white mb-2">
                        {destination.name}
                      </h3>
                      <p className="text-gray-300 mb-4 line-clamp-2">
                        {destination.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-primary-400 font-semibold">
                          {destination.price_range}
                        </span>
                        <Link
                          to={`/destinations/${destination.destination_id}`}
                          className="btn-gradient px-4 py-2 rounded-lg text-sm font-medium hover:shadow-lg transition-all flex items-center gap-2"
                        >
                          Explore
                          <ArrowRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )
          ) : (
            <div className="glass rounded-2xl p-8 border border-white/10">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                    <Lock className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white text-xl font-semibold">Login Required</h3>
                    <p className="text-gray-300">Create an account or sign in to view featured destinations and personalized recommendations.</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Link to="/login" className="btn-gradient px-6 py-3 rounded-lg font-semibold">Login</Link>
                  <Link to="/register" className="px-6 py-3 rounded-lg font-semibold border border-white/20 hover:bg-white/10 transition-colors">Sign Up</Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary-600 to-secondary-600">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Start Your Journey?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join thousands of travelers who have discovered the future of travel with our AI-powered platform
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <Link
                  to="/destinations"
                  className="bg-white text-primary-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <MapPin className="w-5 h-5" />
                  Explore Now
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="bg-white text-primary-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    <Users className="w-5 h-5" />
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="border-2 border-white text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-white hover:text-primary-600 transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    <Calendar className="w-5 h-5" />
                    Login
                  </Link>
                </>
              )}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Home;