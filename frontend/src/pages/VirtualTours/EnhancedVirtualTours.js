import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  Play, 
  Globe, 
  Headphones, 
  Star, 
  MapPin, 
  Clock, 
  Eye, 
  ExternalLink, 
  Volume2, 
  Maximize,
  Search,
  Filter,
  X,
  SkipForward,
  SkipBack,
  Pause,
  VolumeX,
  Settings,
  Share2,
  Download,
  Heart,
  Bookmark,
  Users,
  TrendingUp
} from 'lucide-react';
import { useQuery } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const EnhancedVirtualTours = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTour, setSelectedTour] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Fetch virtual tours
  const { data: tours, isLoading, error } = useQuery(
    ['virtual-tours', searchTerm],
    () => apiService.getVirtualTours({ search: searchTerm }),
    {
      onError: (error) => {
        console.error('Error fetching virtual tours:', error);
        toast.error('Failed to load virtual tours');
      }
    }
  );

  // Fetch featured tours
  const { data: featuredTours } = useQuery(
    'featured-virtual-tours',
    () => apiService.getFeaturedVirtualTours(6),
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  const tourTypes = [
    { id: 'all', label: 'All Tours', icon: Globe, color: 'from-blue-500 to-purple-600' },
    { id: '360_video', label: '360° Videos', icon: Play, color: 'from-green-500 to-emerald-600' },
    { id: 'interactive_360', label: 'Interactive', icon: Eye, color: 'from-orange-500 to-red-600' },
    { id: 'drone_360', label: 'Drone Tours', icon: Camera, color: 'from-purple-500 to-pink-600' },
    { id: 'cultural_360', label: 'Cultural', icon: Users, color: 'from-indigo-500 to-blue-600' }
  ];

  const handleTourClick = (tour) => {
    setSelectedTour(tour);
    setCurrentTime(0);
    setIsPlaying(false);
    toast.success(`Starting virtual tour of ${tour.name}`);
  };

  const closeTour = () => {
    setSelectedTour(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setIsFullscreen(false);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = (time) => {
    setCurrentTime(time);
  };

  const skipToHighlight = (time) => {
    const timeInSeconds = parseFloat(time.split(':')[0]) * 60 + parseFloat(time.split(':')[1]);
    setCurrentTime(timeInSeconds);
    setIsPlaying(true);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const shareTour = (tour) => {
    if (navigator.share) {
      navigator.share({
        title: `Virtual Tour: ${tour.name}`,
        text: tour.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Tour link copied to clipboard!');
    }
  };

  const formatDuration = (duration) => {
    return duration || '0:00';
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredTours = tours?.filter(tour => 
    selectedFilter === 'all' || tour.tour_type === selectedFilter
  ) || [];

  if (error) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Tours</h2>
          <p className="text-gray-300 mb-4">Please try again later</p>
          <button
            onClick={() => window.location.reload()}
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
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Camera className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">Virtual Tours</h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Explore the world's most beautiful destinations through immersive 360° virtual tours and experiences
          </p>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-8"
        >
          {/* Search Bar */}
          <div className="relative max-w-md mx-auto mb-6">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search virtual tours..."
              className="input-futuristic w-full pl-12 pr-4 py-3 rounded-full"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex flex-wrap justify-center gap-4">
            {tourTypes.map((type) => (
              <motion.button
                key={type.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedFilter(type.id)}
                className={`glass rounded-xl p-4 transition-all duration-300 ${
                  selectedFilter === type.id
                    ? 'ring-2 ring-primary-500 bg-primary-500/20'
                    : 'hover:bg-white/10'
                }`}
              >
                <div className={`w-12 h-12 bg-gradient-to-br ${type.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
                  <type.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">{type.label}</h3>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Featured Tours Section */}
        {featuredTours && featuredTours.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="mb-12"
          >
            <h2 className="text-3xl font-bold text-white mb-6 text-center">Featured Tours</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredTours.slice(0, 3).map((tour, index) => (
                <motion.div
                  key={tour.tour_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ y: -5, scale: 1.02 }}
                  className="glass rounded-xl overflow-hidden cursor-pointer group relative"
                  onClick={() => handleTourClick(tour)}
                >
                  <div className="absolute top-2 left-2 z-10">
                    <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-2 py-1 rounded-full text-xs font-bold">
                      FEATURED
                    </span>
                  </div>
                  
                  <div className="relative h-48 overflow-hidden">
                    <img
                      src={tour.thumbnail}
                      alt={tour.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    
                    <div className="absolute top-4 right-4 w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center">
                      <Play className="w-6 h-6 text-white ml-1" />
                    </div>
                    
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-4 h-4 text-gray-300" />
                        <span className="text-white text-sm">{tour.duration}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-2">{tour.name}</h3>
                    <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                      {tour.description}
                    </p>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {tour.features?.slice(0, 3).map((feature, index) => (
                        <span
                          key={`feature-${tour.tour_id || tour.name}-${index}`}
                          className="px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full text-xs"
                        >
                          {feature}
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
                      
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            shareTour(tour);
                          }}
                          className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors"
                        >
                          <Share2 className="w-4 h-4 text-white" />
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTourClick(tour);
                          }}
                          className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors"
                        >
                          <ExternalLink className="w-4 h-4 text-white" />
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* All Tours Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold text-white">All Virtual Tours</h2>
            <div className="text-gray-300 text-sm">
              {filteredTours.length} tours available
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner size="large" text="Loading virtual tours..." />
            </div>
          ) : filteredTours.length === 0 ? (
            <div className="text-center py-20">
              <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-white mb-2">No tours found</h3>
              <p className="text-gray-300 mb-6">Try adjusting your search or filters</p>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedFilter('all');
                }}
                className="btn-gradient px-6 py-3 rounded-lg"
              >
                Clear Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTours.map((tour, index) => (
                <motion.div
                  key={tour.tour_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ y: -5, scale: 1.02 }}
                  className="glass rounded-xl overflow-hidden cursor-pointer group"
                  onClick={() => handleTourClick(tour)}
                >
                  <div className="relative h-48 overflow-hidden">
                    <img
                      src={tour.thumbnail}
                      alt={tour.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    <div className="absolute top-4 left-4 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1">
                      <span className="text-white text-sm font-medium">{tour.country}</span>
                    </div>
                    <div className="absolute top-4 right-4 w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                      <Play className="w-5 h-5 text-white ml-1" />
                    </div>
                    <div className="absolute bottom-4 left-4 right-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4 text-gray-300" />
                          <span className="text-white text-sm">{tour.duration}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <MapPin className="w-4 h-4 text-gray-300" />
                          <span className="text-white text-sm">{tour.country}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-2">{tour.name}</h3>
                    <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                      {tour.description}
                    </p>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {tour.features?.slice(0, 3).map((feature, index) => (
                        <span
                          key={`feature-${tour.tour_id || tour.name}-${index}`}
                          className="px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full text-xs"
                        >
                          {feature}
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
            </div>
          )}
        </motion.div>

        {/* Enhanced Virtual Tour Modal */}
        <AnimatePresence>
          {selectedTour && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className={`fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-sm ${
                isFullscreen ? 'p-0' : 'p-4'
              }`}
              onClick={closeTour}
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.8, opacity: 0 }}
                className={`glass rounded-2xl overflow-hidden ${
                  isFullscreen ? 'w-full h-full rounded-none' : 'max-w-6xl w-full max-h-[90vh]'
                }`}
                onClick={(e) => e.stopPropagation()}
              >
                {/* Tour Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedTour.name}</h2>
                    <p className="text-gray-300">{selectedTour.country}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={toggleFullscreen}
                      className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors"
                    >
                      <Maximize className="w-5 h-5 text-white" />
                    </button>
                    <button
                      onClick={() => shareTour(selectedTour)}
                      className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors"
                    >
                      <Share2 className="w-5 h-5 text-white" />
                    </button>
                    <button
                      onClick={closeTour}
                      className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                    >
                      <X className="w-5 h-5 text-white" />
                    </button>
                  </div>
                </div>

                <div className="flex flex-col lg:flex-row h-full">
                  {/* Video Player */}
                  <div className="flex-1 relative bg-black">
                    <div className="aspect-video bg-gray-800 flex items-center justify-center relative">
                      {/* Embedded YouTube Player */}
                      <iframe
                        src={selectedTour.video_url}
                        title={selectedTour.name}
                        className="w-full h-full"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                      
                      {/* Custom Controls Overlay */}
                      <AnimatePresence>
                        {showControls && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4"
                          >
                            <div className="flex items-center gap-4">
                              <button
                                onClick={togglePlayPause}
                                className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors"
                              >
                                {isPlaying ? (
                                  <Pause className="w-5 h-5 text-white" />
                                ) : (
                                  <Play className="w-5 h-5 text-white ml-1" />
                                )}
                              </button>
                              
                              <div className="flex-1 flex items-center gap-2">
                                <span className="text-white text-sm">{formatTime(currentTime)}</span>
                                <div className="flex-1 bg-gray-600 rounded-full h-1">
                                  <div 
                                    className="bg-primary-500 h-1 rounded-full transition-all"
                                    style={{ width: `${(currentTime / 600) * 100}%` }}
                                  />
                                </div>
                                <span className="text-white text-sm">{selectedTour.duration}</span>
                              </div>
                              
                              <button
                                onClick={toggleMute}
                                className="w-8 h-8 flex items-center justify-center text-white hover:text-primary-400 transition-colors"
                              >
                                {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                              </button>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>

                  {/* Tour Information Sidebar */}
                  <div className="lg:w-80 bg-black/20 p-6 overflow-y-auto">
                    <div className="space-y-6">
                      {/* Tour Details */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">Tour Details</h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-primary-400" />
                            <span className="text-gray-300">Duration: {selectedTour.duration}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Eye className="w-4 h-4 text-primary-400" />
                            <span className="text-gray-300">Type: {selectedTour.tour_type?.replace('_', ' ')}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-primary-400" />
                            <span className="text-gray-300">{selectedTour.country}</span>
                          </div>
                        </div>
                      </div>

                      {/* Features */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">Features</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedTour.features?.map((feature, index) => (
                            <span
                              key={`feature-${selectedTour.tour_id || selectedTour.name}-${index}`}
                              className="px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full text-xs"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Highlights */}
                      {selectedTour.highlights && (
                        <div>
                          <h3 className="text-lg font-semibold text-white mb-3">Tour Highlights</h3>
                          <div className="space-y-3">
                            {selectedTour.highlights.map((highlight, index) => (
                              <div
                                key={index}
                                className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-700/50 transition-colors"
                                onClick={() => skipToHighlight(highlight.time)}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-primary-400 text-sm font-medium">{highlight.time}</span>
                                  <SkipForward className="w-4 h-4 text-gray-400" />
                                </div>
                                <h4 className="text-white font-medium text-sm">{highlight.title}</h4>
                                <p className="text-gray-300 text-xs">{highlight.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Description */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">About</h3>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {selectedTour.description}
                        </p>
                      </div>

                      {/* Interactive Elements */}
                      {selectedTour.interactive_elements && (
                        <div>
                          <h3 className="text-lg font-semibold text-white mb-3">Interactive Elements</h3>
                          <div className="space-y-2">
                            {selectedTour.interactive_elements.map((element, index) => (
                              <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
                                <div className="w-2 h-2 bg-primary-400 rounded-full"></div>
                                <span>{element.info}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EnhancedVirtualTours;