import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPin, 
  Star, 
  Calendar, 
  Users, 
  Camera, 
  Heart, 
  ArrowRight, 
  ArrowLeft,
  Clock,
  DollarSign,
  CloudSun,
  Play,
  Share2,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  MessageCircle,
  ThumbsUp,
  Eye,
  Globe,
  Plane,
  Car,
  Home,
  Phone,
  Mail
} from 'lucide-react';
import { useQuery } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const DestinationDetail = () => {
  const { id } = useParams();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [bookingData, setBookingData] = useState({
    checkIn: '',
    checkOut: '',
    guests: 2,
    specialRequests: ''
  });

  // Fetch destination details
  const { data: destination, isLoading, error } = useQuery(
    ['destination', id],
    () => apiService.getDestination(id),
    {
      enabled: !!id,
      onError: (error) => {
        console.error('Error fetching destination:', error);
        toast.error('Failed to load destination details');
      }
    }
  );

  // Fetch reviews
  const { data: reviews } = useQuery(
    ['reviews', id],
    () => apiService.getDestinationReviews(id),
    {
      enabled: !!id,
      onError: (error) => {
        console.error('Error fetching reviews:', error);
      }
    }
  );

  const handleImageNavigation = (direction) => {
    if (!destination?.images?.length) return;
    
    if (direction === 'next') {
      setCurrentImageIndex((prev) => 
        prev === destination.images.length - 1 ? 0 : prev + 1
      );
    } else {
      setCurrentImageIndex((prev) => 
        prev === 0 ? destination.images.length - 1 : prev - 1
      );
    }
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    try {
      // This would typically require authentication
      const bookingPayload = {
        destination_id: id,
        check_in_date: new Date(bookingData.checkIn).toISOString(),
        check_out_date: new Date(bookingData.checkOut).toISOString(),
        guests: bookingData.guests,
        special_requests: bookingData.specialRequests
      };
      
      // For demo purposes, just show success
      toast.success('Booking request submitted! You will receive confirmation shortly.');
      setShowBookingModal(false);
    } catch (error) {
      toast.error('Please login to make a booking');
    }
  };

  const shareDestination = () => {
    if (navigator.share) {
      navigator.share({
        title: destination?.name,
        text: destination?.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Destination Not Found</h2>
          <p className="text-gray-300 mb-6">The destination you're looking for doesn't exist or has been removed.</p>
          <Link 
            to="/destinations"
            className="btn-gradient px-6 py-3 rounded-lg inline-flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Destinations
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <LoadingSpinner size="large" text="Loading destination details..." />
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'activities', label: 'Activities', icon: Camera },
    { id: 'reviews', label: 'Reviews', icon: MessageCircle },
    { id: 'booking', label: 'Book Now', icon: Calendar }
  ];

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section with Image Gallery */}
      <section className="relative h-96 md:h-[500px] overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentImageIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0"
          >
            <img
              src={destination?.images?.[currentImageIndex] || '/api/placeholder/1200/500'}
              alt={destination?.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
          </motion.div>
        </AnimatePresence>

        {/* Image Navigation */}
        {destination?.images?.length > 1 && (
          <>
            <button
              onClick={() => handleImageNavigation('prev')}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
            >
              <ChevronLeft className="w-6 h-6 text-white" />
            </button>
            <button
              onClick={() => handleImageNavigation('next')}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-black/70 transition-colors"
            >
              <ChevronRight className="w-6 h-6 text-white" />
            </button>
          </>
        )}

        {/* Image Indicators */}
        {destination?.images?.length > 1 && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
            {destination.images.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentImageIndex(index)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}

        {/* Header Content */}
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <MapPin className="w-5 h-5 text-primary-400" />
                <span className="text-primary-400 font-medium">{destination?.city}, {destination?.country}</span>
              </div>
              
              <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
                {destination?.name}
              </h1>
              
              <div className="flex items-center gap-6 mb-6">
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400 fill-current" />
                  <span className="text-white font-semibold">{destination?.rating}</span>
                  <span className="text-gray-300">({reviews?.length || 0} reviews)</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-400" />
                  <span className="text-green-400 font-semibold">{destination?.price_range}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setShowBookingModal(true)}
                  className="btn-gradient px-8 py-3 rounded-lg font-semibold hover:shadow-glow transition-all flex items-center gap-2"
                >
                  <Calendar className="w-5 h-5" />
                  Book Now
                </button>
                
                <button
                  onClick={() => setIsLiked(!isLiked)}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                    isLiked ? 'bg-red-500 text-white' : 'bg-black/50 text-white hover:bg-black/70'
                  }`}
                >
                  <Heart className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} />
                </button>
                
                <button
                  onClick={() => setIsBookmarked(!isBookmarked)}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
                    isBookmarked ? 'bg-blue-500 text-white' : 'bg-black/50 text-white hover:bg-black/70'
                  }`}
                >
                  <Bookmark className={`w-5 h-5 ${isBookmarked ? 'fill-current' : ''}`} />
                </button>
                
                <button
                  onClick={shareDestination}
                  className="w-12 h-12 bg-black/50 rounded-full flex items-center justify-center text-white hover:bg-black/70 transition-colors"
                >
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Navigation Tabs */}
      <section className="bg-black/20 sticky top-20 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                    selectedTab === tab.id
                      ? 'text-primary-400 border-b-2 border-primary-400'
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* Content Sections */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          {selectedTab === 'overview' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-8">
                {/* Description */}
                <div className="glass rounded-2xl p-6">
                  <h2 className="text-2xl font-bold text-white mb-4">About This Destination</h2>
                  <p className="text-gray-300 leading-relaxed">{destination?.description}</p>
                </div>

                {/* Weather */}
                {destination?.weather && (
                  <div className="glass rounded-2xl p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <CloudSun className="w-5 h-5 text-yellow-400" />
                      Current Weather
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {destination.weather.main && (
                        <>
                          <div className="text-center">
                            <p className="text-gray-400 text-sm">Temperature</p>
                            <p className="text-white font-semibold">{Math.round(destination.weather.main.temp)}°C</p>
                          </div>
                          <div className="text-center">
                            <p className="text-gray-400 text-sm">Feels Like</p>
                            <p className="text-white font-semibold">{Math.round(destination.weather.main.feels_like)}°C</p>
                          </div>
                          <div className="text-center">
                            <p className="text-gray-400 text-sm">Humidity</p>
                            <p className="text-white font-semibold">{destination.weather.main.humidity}%</p>
                          </div>
                          <div className="text-center">
                            <p className="text-gray-400 text-sm">Condition</p>
                            <p className="text-white font-semibold">{destination.weather.weather?.[0]?.main}</p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}

                {/* Virtual Tour */}
                {destination?.virtual_tour_url && (
                  <div className="glass rounded-2xl p-6">
                    <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                      <Globe className="w-5 h-5 text-primary-400" />
                      Virtual Tour
                    </h3>
                    <div className="relative aspect-video bg-gradient-to-br from-primary-900/20 to-secondary-900/20 rounded-lg flex items-center justify-center">
                      <button className="w-20 h-20 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors">
                        <Play className="w-8 h-8 text-white ml-1" />
                      </button>
                    </div>
                    <p className="text-gray-300 mt-4">Take a virtual tour of this amazing destination from the comfort of your home.</p>
                  </div>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Quick Info */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Quick Info</h3>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Clock className="w-5 h-5 text-primary-400" />
                      <div>
                        <p className="text-gray-400 text-sm">Best Time to Visit</p>
                        <p className="text-white">{destination?.best_time_to_visit}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <DollarSign className="w-5 h-5 text-green-400" />
                      <div>
                        <p className="text-gray-400 text-sm">Price Range</p>
                        <p className="text-white">{destination?.price_range}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5 text-red-400" />
                      <div>
                        <p className="text-gray-400 text-sm">Location</p>
                        <p className="text-white">{destination?.city}, {destination?.country}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Contact Info */}
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Contact & Support</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 text-gray-300">
                      <Phone className="w-4 h-4 text-primary-400" />
                      <span>+1 (555) 123-4567</span>
                    </div>
                    <div className="flex items-center gap-3 text-gray-300">
                      <Mail className="w-4 h-4 text-primary-400" />
                      <span>info@travelplatform.com</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {selectedTab === 'activities' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="glass rounded-2xl p-6"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Activities & Experiences</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {destination?.activities?.map((activity, index) => (
                  <div key={index} className="bg-gradient-to-br from-primary-900/20 to-secondary-900/20 rounded-lg p-4 border border-white/10">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
                        <Camera className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-white font-semibold">{activity}</h3>
                    </div>
                    <p className="text-gray-300 text-sm">Experience amazing {activity.toLowerCase()} activities in this destination.</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {selectedTab === 'reviews' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="glass rounded-2xl p-6"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Reviews & Ratings</h2>
              {reviews?.length > 0 ? (
                <div className="space-y-6">
                  {reviews.map((review, index) => (
                    <div key={index} className="border-b border-white/10 pb-6 last:border-b-0">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-semibold">{review.username?.[0]?.toUpperCase()}</span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="text-white font-semibold">{review.username}</h4>
                            <div className="flex items-center gap-1">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-4 h-4 ${
                                    i < review.rating ? 'text-yellow-400 fill-current' : 'text-gray-600'
                                  }`}
                                />
                              ))}
                            </div>
                          </div>
                          <p className="text-gray-300">{review.comment}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">No Reviews Yet</h3>
                  <p className="text-gray-300">Be the first to review this amazing destination!</p>
                </div>
              )}
            </motion.div>
          )}

          {selectedTab === 'booking' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="glass rounded-2xl p-6"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Book Your Experience</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <form onSubmit={handleBooking} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Check-in Date</label>
                        <input
                          type="date"
                          value={bookingData.checkIn}
                          onChange={(e) => setBookingData({...bookingData, checkIn: e.target.value})}
                          className="input-futuristic w-full"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Check-out Date</label>
                        <input
                          type="date"
                          value={bookingData.checkOut}
                          onChange={(e) => setBookingData({...bookingData, checkOut: e.target.value})}
                          className="input-futuristic w-full"
                          required
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Number of Guests</label>
                      <select
                        value={bookingData.guests}
                        onChange={(e) => setBookingData({...bookingData, guests: parseInt(e.target.value)})}
                        className="input-futuristic w-full"
                      >
                        {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                          <option key={num} value={num}>{num} Guest{num > 1 ? 's' : ''}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Special Requests</label>
                      <textarea
                        value={bookingData.specialRequests}
                        onChange={(e) => setBookingData({...bookingData, specialRequests: e.target.value})}
                        className="input-futuristic w-full"
                        rows={4}
                        placeholder="Any special requirements or requests..."
                      />
                    </div>
                    
                    <button
                      type="submit"
                      className="btn-gradient w-full py-3 rounded-lg font-semibold hover:shadow-glow transition-all"
                    >
                      Book Now - {destination?.price_range}
                    </button>
                  </form>
                </div>
                
                <div className="space-y-6">
                  <div className="bg-gradient-to-br from-primary-900/20 to-secondary-900/20 rounded-lg p-6 border border-white/10">
                    <h3 className="text-xl font-semibold text-white mb-4">What's Included</h3>
                    <ul className="space-y-2 text-gray-300">
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        Accommodation
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        Transportation
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        Guided Tours
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        24/7 Support
                      </li>
                    </ul>
                  </div>
                  
                  <div className="bg-gradient-to-br from-secondary-900/20 to-primary-900/20 rounded-lg p-6 border border-white/10">
                    <h3 className="text-xl font-semibold text-white mb-4">Cancellation Policy</h3>
                    <p className="text-gray-300 text-sm">
                      Free cancellation up to 48 hours before your trip. 
                      Cancellations within 48 hours are subject to a 25% fee.
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* Booking Modal */}
      <AnimatePresence>
        {showBookingModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            onClick={() => setShowBookingModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass rounded-2xl p-6 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold text-white mb-4">Quick Booking</h3>
              <p className="text-gray-300 mb-6">
                Ready to book {destination?.name}? Use the booking tab above for detailed options or contact us directly.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => {setShowBookingModal(false); setSelectedTab('booking');}}
                  className="btn-gradient flex-1 py-3 rounded-lg font-semibold"
                >
                  Book Now
                </button>
                <button
                  onClick={() => setShowBookingModal(false)}
                  className="glass flex-1 py-3 rounded-lg font-semibold hover:bg-white/10"
                >
                  Later
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DestinationDetail;