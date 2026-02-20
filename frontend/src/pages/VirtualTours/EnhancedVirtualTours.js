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
  X,
  SkipForward,
  Pause,
  VolumeX,
  Share2,
  Heart,
  Bookmark,
  List,
  Compass,
  Radio,
  Plane
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';

const EnhancedVirtualTours = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTour, setSelectedTour] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const [currentSlide, setCurrentSlide] = useState(0);
  const [playerError, setPlayerError] = useState(null);
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [narrationText, setNarrationText] = useState('');
  const [isNarrating, setIsNarrating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const playerRef = useRef(null);

  const categories = [
    { id: 'all', label: 'All Experiences', icon: Globe },
    { id: '360_video', label: '360° Tours', icon: Compass },
    { id: 'live_cam', label: 'Live Cams', icon: Radio },
    { id: 'drone_video', label: 'Drone Views', icon: Plane },
  ];



  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuth();

  // Fetch virtual tours list
  const { data: toursData, isLoading, error } = useQuery(
    ['virtual-tours', searchTerm, activeCategory],
    () => apiService.getVirtualTours({ search: searchTerm }), // Client-side filtering for now since backend mock is simple
    { keepPreviousData: true }
  );

  const tours = toursData?.items || [];

  // Fetch featured tours
  const { data: featuredTours } = useQuery(
    'featured-virtual-tours',
    () => apiService.getFeaturedVirtualTours(6),
    { staleTime: 10 * 60 * 1000 }
  );

  // Auto-advance carousel
  useEffect(() => {
    if (!featuredTours || featuredTours.length === 0) return;
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % Math.min(featuredTours.length, 5));
    }, 6000);
    return () => clearInterval(interval);
  }, [featuredTours]);

  // Favorites
  const { data: favoritesData, refetch: refetchFavorites } = useQuery(
    'favorite-virtual-tours',
    () => apiService.listFavoriteVirtualTours(),
    { enabled: isAuthenticated }
  );

  const favoriteIds = new Set((favoritesData?.items || []).map((t) => t.tour_id));

  const favoriteMutation = useMutation(
    (tour) => (
      favoriteIds.has(tour.tour_id)
        ? apiService.unfavoriteVirtualTour(tour.tour_id)
        : apiService.favoriteVirtualTour(tour.tour_id)
    ),
    {
      onSuccess: () => {
        refetchFavorites();
        queryClient.invalidateQueries('favorite-virtual-tours');
        toast.success('Updated favorites');
      },
      onError: () => toast.error('Failed to update favorites'),
    }
  );

  // Modal controls
  const handleTourClick = (tour) => {
    setSelectedTour(tour);
    setCurrentTime(0);
    setIsPlaying(false);
    setPlayerError(null);
    setNarrationText('');
  };

  const closeTour = () => {
    setSelectedTour(null);
    setIsPlaying(false);
    setCurrentTime(0);
    setIsFullscreen(false);
    setNarrationText('');
  };

  const togglePlayPause = () => {
    setIsPlaying((prev) => {
      const next = !prev;
      try {
        const iframe = playerRef.current;
        if (iframe && iframe.contentWindow) {
          const cmd = next ? 'playVideo' : 'pauseVideo';
          iframe.contentWindow.postMessage(JSON.stringify({ event: 'command', func: cmd, args: [] }), '*');
        }
      } catch { }
      return next;
    });
  };

  const skipToHighlight = (time) => {
    const [m, s] = time.split(':').map((x) => parseFloat(x));
    const timeInSeconds = (m || 0) * 60 + (s || 0);
    setCurrentTime(timeInSeconds);
    setIsPlaying(true);
  };

  const toggleMute = () => setIsMuted(!isMuted);

  const formatYouTubeEmbedUrl = (url) => {
    if (!url) return '';
    if (url.includes('youtube.com/embed/')) return url;
    try {
      const u = new URL(url);
      if (u.hostname.includes('youtube.com')) {
        const vid = u.searchParams.get('v');
        if (vid) return `https://www.youtube.com/embed/${vid}`;
        const parts = u.pathname.split('/');
        const idx = parts.indexOf('embed');
        if (idx !== -1 && parts[idx + 1]) return `https://www.youtube.com/embed/${parts[idx + 1]}`;
      } else if (u.hostname === 'youtu.be') {
        const vid = u.pathname.replace('/', '');
        if (vid) return `https://www.youtube.com/embed/${vid}`;
      }
    } catch { }
    return url;
  };

  /* Filter Logic with activeCategory */
  const filteredTours = (tours || []).filter(tour => {
    if (favoritesOnly) return favoriteIds.has(tour.tour_id);
    if (activeCategory === 'all') return true;
    // Map backend types if needed, or simple match
    if (activeCategory === '360_video') return tour.tour_type === '360_video' || tour.tour_type === 'drone_360';
    if (activeCategory === 'live_cam') return tour.tour_type === 'live_cam';
    if (activeCategory === 'drone_video') return tour.tour_type === 'drone_video';
    return true;
  });

  const handleToggleFavorite = (tour) => {
    if (!isAuthenticated) {
      toast.error('Please login to save favorites');
      return;
    }
    favoriteMutation.mutate(tour);
  };

  const handleNarrate = async () => {
    if (!isAuthenticated) {
      toast.error('Please login to use AI narration');
      return;
    }
    if (!selectedTour) return;
    setIsNarrating(true);
    setNarrationText('');
    try {
      const res = await apiService.narrateVirtualTour(selectedTour.tour_id, {
        voice_style: 'friendly',
        pace: 'medium',
        duration_hint: 'short',
        language: 'en'
      });
      setNarrationText(res.narration || '');
      if ('speechSynthesis' in window && res.narration) {
        const utter = new SpeechSynthesisUtterance(res.narration);
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
      }
    } catch (e) {
      toast.error('Failed to generate narration');
    } finally {
      setIsNarrating(false);
    }
  };

  const stopNarration = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  if (error) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Error Loading Tours</h2>
          <p className="text-gray-300 mb-4">Please try again later</p>
          <button onClick={() => window.location.reload()} className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
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
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Camera className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">Virtual Tours</h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">Explore the world's most beautiful destinations through immersive 360° virtual tours and experiences</p>
        </motion.div>

        {/* Search and Favorites Toggle */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }} className="mb-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="relative max-w-md w-full">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search virtual tours..." className="input-futuristic w-full pl-12 pr-4 py-3 rounded-full" />
            </div>
            <button onClick={() => setFavoritesOnly(!favoritesOnly)} className={`px-4 py-2 rounded-full flex items-center gap-2 ${favoritesOnly ? 'bg-primary-500 text-white' : 'bg-gray-800 text-gray-200 hover:bg-gray-700'}`}>
              <Heart className="w-4 h-4" /> {favoritesOnly ? 'Showing Favorites' : 'My Favorites'}
            </button>
          </div>
        </motion.div>

        {/* Hero Carousel */}
        {featuredTours && featuredTours.length > 0 && (
          <div className="relative h-[500px] w-full rounded-3xl overflow-hidden mb-16 shadow-2xl group">
            <AnimatePresence mode='wait'>
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.8 }}
                className="absolute inset-0"
              >
                <img
                  src={featuredTours[currentSlide]?.thumbnail}
                  alt={featuredTours[currentSlide]?.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />

                <div className="absolute bottom-0 left-0 p-12 w-full max-w-4xl">
                  <div className="flex items-center gap-3 mb-4">
                    {featuredTours[currentSlide]?.tour_type === 'live_cam' && (
                      <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse flex items-center gap-2">
                        <div className="w-2 h-2 bg-white rounded-full" /> LIVE
                      </span>
                    )}
                    <span className="bg-primary-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                      Featured
                    </span>
                  </div>
                  <h2 className="text-5xl font-bold text-white mb-4 leading-tight">
                    {featuredTours[currentSlide]?.name}
                  </h2>
                  <p className="text-xl text-gray-200 mb-8 line-clamp-2 max-w-2xl">
                    {featuredTours[currentSlide]?.description}
                  </p>
                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => handleTourClick(featuredTours[currentSlide])}
                      className="bg-white text-black px-8 py-3 rounded-full font-bold flex items-center gap-2 hover:bg-gray-100 transition-colors"
                    >
                      <Play className="w-5 h-5 fill-black" /> Start Experience
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleToggleFavorite(featuredTours[currentSlide]); }}
                      className={`w-12 h-12 rounded-full flex items-center justify-center border-2 border-white/30 backdrop-blur-sm hover:bg-white/10 transition-colors ${favoriteIds.has(featuredTours[currentSlide]?.tour_id) ? 'bg-red-500 border-red-500' : ''}`}
                    >
                      <Heart className={`w-6 h-6 ${favoriteIds.has(featuredTours[currentSlide]?.tour_id) ? 'fill-white text-white' : 'text-white'}`} />
                    </button>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Carousel Indicators */}
            <div className="absolute bottom-6 right-6 flex gap-2 z-10">
              {featuredTours.slice(0, 5).map((_, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentSlide(idx)}
                  className={`w-3 h-3 rounded-full transition-all ${currentSlide === idx ? 'bg-white w-8' : 'bg-white/50 hover:bg-white'}`}
                />
              ))}
            </div>
          </div>
        )}

        {/* Filters & Grid */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}>
          {/* Category Tabs */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => { setActiveCategory(cat.id); setFavoritesOnly(false); }}
                className={`px-6 py-3 rounded-full flex items-center gap-2 transition-all ${activeCategory === cat.id && !favoritesOnly
                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg scale-105'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                  }`}
              >
                <cat.icon className="w-5 h-5" />
                {cat.label}
              </button>
            ))}
          </div>

          <div className="flex items-center justify-between mb-8">
            <h3 className="text-2xl font-bold text-white">
              {favoritesOnly ? 'Your Favorites' : (categories.find(c => c.id === activeCategory)?.label || 'All Experiences')}
            </h3>
            <button
              onClick={() => setFavoritesOnly(!favoritesOnly)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${favoritesOnly ? 'text-red-400' : 'text-gray-400 hover:text-white'}`}
            >
              <Heart className={`w-5 h-5 ${favoritesOnly ? 'fill-current' : ''}`} />
              <span>{favoritesOnly ? 'Show All' : 'Show Favorites'}</span>
            </button>
          </div>


          {isLoading ? (
            <div className="flex justify-center py-20"><LoadingSpinner size="large" text="Loading virtual tours..." /></div>
          ) : filteredTours.length === 0 ? (
            <div className="text-center py-20">
              <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-white mb-2">No tours found</h3>
              <p className="text-gray-300 mb-6">Try adjusting your search or filters</p>
              <button onClick={() => { setSearchTerm(''); setActiveCategory('all'); setFavoritesOnly(false); }} className="btn-gradient px-6 py-3 rounded-lg">Clear Filters</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTours.map((tour, index) => (
                <motion.div key={tour.tour_id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: index * 0.05 }} whileHover={{ y: -5, scale: 1.02 }} className="glass rounded-xl overflow-hidden cursor-pointer group" onClick={() => handleTourClick(tour)}>
                  <div className="relative h-48 overflow-hidden">
                    <img src={tour.thumbnail} alt={tour.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                    <div className="absolute top-4 left-4 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1"><span className="text-white text-sm font-medium">{tour.country}</span></div>
                    <div className="absolute top-4 right-4 w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center"><Play className="w-5 h-5 text-white ml-1" /></div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-2">{tour.name}</h3>
                    <p className="text-gray-300 text-sm mb-4 line-clamp-2">{tour.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        <div className="flex items-center gap-1"><Clock className="w-4 h-4" /><span>{tour.duration}</span></div>
                        <div className="flex items-center gap-1"><MapPin className="w-4 h-4" /><span>{tour.country}</span></div>
                      </div>
                      <button onClick={(e) => { e.stopPropagation(); handleToggleFavorite(tour); }} className={`w-8 h-8 rounded-full flex items-center justify-center ${favoriteIds.has(tour.tour_id) ? 'bg-red-500' : 'bg-gray-700 hover:bg-gray-600'}`}>
                        <Heart className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Virtual Tour Modal */}
        <AnimatePresence>
          {selectedTour && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className={`fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-sm ${isFullscreen ? 'p-0' : 'p-4'}`} onClick={closeTour}>
              <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }} className={`glass rounded-2xl overflow-hidden ${isFullscreen ? 'w-full h-full rounded-none' : 'max-w-6xl w-full max-h-[90vh]'}`} onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedTour.name}</h2>
                    <p className="text-gray-300">{selectedTour.country}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleToggleFavorite(selectedTour)} className={`w-10 h-10 rounded-full flex items-center justify-center ${favoriteIds.has(selectedTour.tour_id) ? 'bg-red-500' : 'bg-gray-700 hover:bg-gray-600'}`} title="Favorite">
                      <Heart className="w-5 h-5 text-white" />
                    </button>
                    <button onClick={() => setIsFullscreen(!isFullscreen)} className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors" title="Fullscreen">
                      <Maximize className="w-5 h-5 text-white" />
                    </button>
                    <button onClick={() => navigator.clipboard.writeText(window.location.href)} className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors" title="Share">
                      <Share2 className="w-5 h-5 text-white" />
                    </button>
                    <button onClick={closeTour} className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors" title="Close">
                      <X className="w-5 h-5 text-white" />
                    </button>
                  </div>
                </div>

                <div className="flex flex-col lg:flex-row h-full">
                  {/* Player */}
                  <div className="flex-1 relative bg-black">
                    <div className="aspect-video bg-gray-800 flex items-center justify-center relative">
                      <iframe src={`${formatYouTubeEmbedUrl(selectedTour.video_url)}?enablejsapi=1&rel=0&modestbranding=1&playsinline=1&origin=${encodeURIComponent(window.location.origin)}`} title={selectedTour.name} ref={playerRef} className="w-full h-full" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen onLoad={() => { setPlayerError(null); }} onError={() => { setPlayerError('unavailable'); }} />

                      {playerError === 'unavailable' && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-center p-6">
                          <Camera className="w-12 h-12 text-gray-300 mb-3" />
                          <h4 className="text-white font-semibold mb-2">Video unavailable</h4>
                          <p className="text-gray-300 text-sm mb-4 max-w-md">This video can't be embedded due to content restrictions. You can still watch it directly on YouTube.</p>
                          <a href={formatYouTubeEmbedUrl(selectedTour.video_url).replace('/embed/', '/watch?v=')} target="_blank" rel="noreferrer" className="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white">Open on YouTube</a>
                        </div>
                      )}

                      {/* Controls */}
                      <AnimatePresence>
                        {showControls && (
                          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                            <div className="flex items-center gap-4">
                              <button onClick={togglePlayPause} className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors">
                                {isPlaying ? (<Pause className="w-5 h-5 text-white" />) : (<Play className="w-5 h-5 text-white ml-1" />)}
                              </button>
                              <div className="flex-1 flex items-center gap-2">
                                <span className="text-white text-sm">
                                  {selectedTour.tour_type === 'live_cam' ? 'LIVE' : `${Math.floor(currentTime / 60)}:${String(Math.floor(currentTime % 60)).padStart(2, '0')}`}
                                </span>
                                {selectedTour.tour_type !== 'live_cam' && (
                                  <div className="flex-1 bg-gray-600 rounded-full h-1">
                                    <div className="bg-primary-500 h-1 rounded-full transition-all" style={{ width: `${(currentTime / 600) * 100}%` }} />
                                  </div>
                                )}
                                {selectedTour.tour_type === 'live_cam' && (
                                  <span className="flex-1 text-red-500 font-bold text-xs tracking-widest animate-pulse ml-2">• LIVE BROADCAST</span>
                                )}
                                <span className="text-white text-sm">{selectedTour.duration}</span>
                              </div>
                              <button onClick={toggleMute} className="w-8 h-8 flex items-center justify-center text-white hover:text-primary-400 transition-colors">
                                {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                              </button>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>

                  {/* Sidebar */}
                  <div className="lg:w-96 bg-black/20 p-6 overflow-y-auto">
                    <div className="space-y-6">
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">Tour Details</h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2"><Clock className="w-4 h-4 text-primary-400" /><span className="text-gray-300">Duration: {selectedTour.duration}</span></div>
                          <div className="flex items-center gap-2"><Eye className="w-4 h-4 text-primary-400" /><span className="text-gray-300">Type: {selectedTour.tour_type?.replace('_', ' ')}</span></div>
                          <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-primary-400" /><span className="text-gray-300">{selectedTour.country}</span></div>
                        </div>
                      </div>

                      {/* Features */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">Features</h3>
                        <div className="flex flex-wrap gap-2">
                          {selectedTour.features?.map((feature, index) => (
                            <span key={`feature-${selectedTour.tour_id}-${index}`} className="px-2 py-1 bg-primary-500/20 text-primary-300 rounded-full text-xs">{feature}</span>
                          ))}
                        </div>
                      </div>

                      {/* Highlights */}
                      {selectedTour.highlights && (
                        <div>
                          <h3 className="text-lg font-semibold text-white mb-3">Tour Highlights</h3>
                          <div className="space-y-3">
                            {selectedTour.highlights.map((highlight, index) => (
                              <div key={index} className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-700/50 transition-colors" onClick={() => skipToHighlight(highlight.time)}>
                                <div className="flex items-center justify-between mb-1"><span className="text-primary-400 text-sm font-medium">{highlight.time}</span></div>
                                <h4 className="text-white font-medium text-sm">{highlight.title}</h4>
                                <p className="text-gray-300 text-xs">{highlight.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* AI Narration */}
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-3">AI Narration</h3>
                        <div className="flex items-center gap-2 mb-3">
                          <button onClick={handleNarrate} disabled={isNarrating} className="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white disabled:opacity-50">{isNarrating ? 'Generating...' : 'Generate Narration'}</button>
                          <button onClick={stopNarration} className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white">Stop</button>
                        </div>
                        {narrationText && (
                          <div className="p-3 bg-gray-800/50 rounded-lg text-sm text-gray-200 whitespace-pre-wrap">
                            {narrationText}
                          </div>
                        )}
                      </div>
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