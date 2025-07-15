import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Camera, Play, Globe, Headphones, Star, MapPin, Clock, Eye, ExternalLink, Volume2, Maximize } from 'lucide-react';
import { toast } from 'react-hot-toast';

const VirtualTours = () => {
  const [destinations, setDestinations] = useState([]);
  const [selectedTour, setSelectedTour] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFeature, setActiveFeature] = useState('all');

  useEffect(() => {
    fetchDestinations();
  }, []);

  const fetchDestinations = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/destinations/featured`);
      if (!response.ok) {
        throw new Error('Failed to fetch destinations');
      }
      const data = await response.json();
      setDestinations(data);
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load virtual tours');
    } finally {
      setLoading(false);
    }
  };

  const handleTourClick = (destination) => {
    setSelectedTour(destination);
    toast.success(`Starting virtual tour of ${destination.name}`);
  };

  const closeTour = () => {
    setSelectedTour(null);
  };

  const features = [
    {
      id: 'all',
      icon: Globe,
      title: 'All Tours',
      description: 'Explore all virtual destinations',
      color: 'from-blue-500 to-purple-600'
    },
    {
      id: '360',
      icon: Play,
      title: '360° Videos',
      description: 'Immersive video experiences',
      color: 'from-green-500 to-emerald-600'
    },
    {
      id: 'vr',
      icon: Eye,
      title: 'VR Ready',
      description: 'Virtual reality compatibility',
      color: 'from-orange-500 to-red-600'
    },
    {
      id: 'audio',
      icon: Headphones,
      title: 'Audio Guide',
      description: 'Professional narration',
      color: 'from-purple-500 to-pink-600'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-300">Loading virtual tours...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Tours</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={fetchDestinations}
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-7xl mx-auto px-4 py-12"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 100 }}
            className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6"
          >
            <Camera className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-5xl font-bold text-white mb-4">Virtual Tours</h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Explore the world's most beautiful destinations through immersive 360° virtual tours and experiences
          </p>
        </div>

        {/* Features Filter */}
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {features.map((feature) => (
            <motion.button
              key={feature.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveFeature(feature.id)}
              className={`glass rounded-xl p-4 transition-all duration-300 ${
                activeFeature === feature.id
                  ? 'ring-2 ring-primary-500 bg-primary-500/20'
                  : 'hover:bg-white/10'
              }`}
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-sm font-semibold text-white mb-1">{feature.title}</h3>
              <p className="text-xs text-gray-300">{feature.description}</p>
            </motion.button>
          ))}
        </div>

        {/* Virtual Tours Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {destinations.map((destination) => (
            <motion.div
              key={destination.destination_id}
              variants={itemVariants}
              whileHover={{ y: -5, scale: 1.02 }}
              className="glass rounded-xl overflow-hidden cursor-pointer group"
              onClick={() => handleTourClick(destination)}
            >
              <div className="relative h-48 overflow-hidden">
                <img
                  src={destination.images[0]}
                  alt={destination.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                <div className="absolute top-4 left-4 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1">
                  <span className="text-white text-sm font-medium">{destination.country}</span>
                </div>
                <div className="absolute top-4 right-4 w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                  <Play className="w-5 h-5 text-white ml-1" />
                </div>
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-white text-sm font-medium">{destination.rating}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4 text-gray-300" />
                      <span className="text-white text-sm">{destination.city}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2">{destination.name}</h3>
                <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                  {destination.description}
                </p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {destination.activities.slice(0, 3).map((activity, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full text-xs"
                    >
                      {activity}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      <span>360° View</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Volume2 className="w-4 h-4" />
                      <span>Audio Guide</span>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4 text-white" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Virtual Tour Modal */}
        {selectedTour && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
            onClick={closeTour}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="glass rounded-2xl p-8 max-w-4xl mx-4 max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold text-white">{selectedTour.name} Virtual Tour</h2>
                <button
                  onClick={closeTour}
                  className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                >
                  <span className="text-white text-xl">×</span>
                </button>
              </div>

              <div className="aspect-video bg-gray-800 rounded-xl mb-6 flex items-center justify-center">
                <div className="text-center">
                  <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl text-white mb-2">360° Virtual Tour</h3>
                  <p className="text-gray-300 mb-4">
                    Experience {selectedTour.name} in immersive 360° view
                  </p>
                  <button className="px-8 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2 mx-auto">
                    <Play className="w-5 h-5" />
                    Start Virtual Tour
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">About this destination</h3>
                  <p className="text-gray-300 text-sm mb-4">{selectedTour.description}</p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-primary-400" />
                      <span className="text-gray-300 text-sm">{selectedTour.city}, {selectedTour.country}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-primary-400" />
                      <span className="text-gray-300 text-sm">{selectedTour.best_time_to_visit}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-gray-300 text-sm">{selectedTour.rating}/5 rating</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">What you can do</h3>
                  <div className="space-y-2">
                    {selectedTour.activities.map((activity, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary-400 rounded-full"></div>
                        <span className="text-gray-300 text-sm">{activity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <Eye className="w-5 h-5 text-primary-400" />
                      <span className="text-gray-300 text-sm">360° Experience</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Volume2 className="w-5 h-5 text-primary-400" />
                      <span className="text-gray-300 text-sm">Audio Guide</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Maximize className="w-5 h-5 text-primary-400" />
                      <span className="text-gray-300 text-sm">Full Screen</span>
                    </div>
                  </div>
                  <button className="px-6 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all">
                    View Destination Details
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default VirtualTours;