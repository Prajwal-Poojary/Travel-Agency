import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  MapPin,
  Users,
  Clock,
  CreditCard,
  CheckCircle,
  XCircle,
  AlertCircle,
  Filter,
  Search,
  Download,
  Eye,
  Edit,
  Trash2,
  Star,
  Phone,
  Mail,
  MessageCircle
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const EnhancedBookings = () => {
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const queryClient = useQueryClient();
  // Review State
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');

  // Fetch user bookings
  const { data: bookings, isLoading, error } = useQuery(
    'user-bookings',
    apiService.getUserBookings,
    {
      enabled: isAuthenticated,
      onError: (error) => {
        console.error('Error fetching bookings:', error);
        toast.error('Failed to load bookings');
      }
    }
  );

  // Cancel booking mutation
  const cancelBookingMutation = useMutation(
    (bookingId) => apiService.cancelBooking(bookingId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('user-bookings');
        toast.success('Booking cancelled successfully');
        setShowCancelModal(false);
        setSelectedBooking(null);
      },
      onError: (error) => {
        toast.error('Failed to cancel booking');
      }
    }
  );

  const statusOptions = [
    { value: 'all', label: 'All Bookings', color: 'bg-gray-500' },
    { value: 'pending', label: 'Pending', color: 'bg-yellow-500' },
    { value: 'confirmed', label: 'Confirmed', color: 'bg-green-500' },
    { value: 'cancelled', label: 'Cancelled', color: 'bg-red-500' },
    { value: 'completed', label: 'Completed', color: 'bg-blue-500' }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'pending':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'cancelled':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'completed':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const filteredBookings = bookings?.filter(booking => {
    const matchesStatus = selectedStatus === 'all' || booking.status === selectedStatus;
    const matchesSearch = !searchTerm ||
      booking.destination_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.destination_details?.city?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.destination_details?.country?.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesStatus && matchesSearch;
  }) || [];

  const handleCancelBooking = (booking) => {
    setSelectedBooking(booking);
    setShowCancelModal(true);
  };

  const confirmCancelBooking = () => {
    if (selectedBooking) {
      cancelBookingMutation.mutate(selectedBooking.booking_id);
    }
  };

  const exportBookings = () => {
    const bookingData = filteredBookings.map(booking => ({
      id: booking.booking_id,
      destination: booking.destination_name,
      checkIn: booking.check_in_date,
      checkOut: booking.check_out_date,
      guests: booking.guests,
      status: booking.status,
      totalAmount: booking.total_amount,
      createdAt: booking.created_at
    }));

    const blob = new Blob([JSON.stringify(bookingData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bookings-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Review Logic
  const handleOpenReview = (booking) => {
    setSelectedBooking(booking);
    setReviewRating(5);
    setReviewComment('');
    setShowReviewModal(true);
  };

  const submitReview = async () => {
    if (!selectedBooking) return;
    try {
      await apiService.createReview({
        destination_id: selectedBooking.destination_id || 'unknown', // Ensure we have destination_id
        rating: reviewRating,
        comment: reviewComment
      });
      toast.success('Review submitted successfully!');
      setShowReviewModal(false);
      setSelectedBooking(null);
    } catch (error) {
      console.error("Review Error:", error);
      toast.error('Failed to submit review');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Calendar className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Login Required</h2>
          <p className="text-gray-300 mb-6">Please login to view your bookings</p>
          <a
            href="/login"
            className="btn-gradient px-6 py-3 rounded-lg inline-flex items-center gap-2"
          >
            Login Now
          </a>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <XCircle className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Error Loading Bookings</h2>
          <p className="text-gray-300 mb-6">Please try again later</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-gradient px-6 py-3 rounded-lg"
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
          className="text-center mb-8"
        >
          <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Calendar className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">My Bookings</h1>
          <p className="text-gray-300">Manage your travel bookings and reservations</p>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="glass rounded-2xl p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search bookings..."
                className="input-futuristic w-full pl-10 pr-4 py-2 rounded-lg"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="input-futuristic px-3 py-2 rounded-lg"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Export Button */}
            <button
              onClick={exportBookings}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            {statusOptions.slice(1).map(status => {
              const count = bookings?.filter(b => b.status === status.value).length || 0;
              return (
                <div key={status.value} className="text-center">
                  <div className={`w-3 h-3 ${status.color} rounded-full mx-auto mb-1`}></div>
                  <div className="text-2xl font-bold text-white">{count}</div>
                  <div className="text-gray-300 text-sm">{status.label}</div>
                </div>
              );
            })}
          </div>
        </motion.div>

        {/* Bookings List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          {isLoading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner size="large" text="Loading your bookings..." />
            </div>
          ) : filteredBookings.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calendar className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                {bookings?.length === 0 ? 'No bookings yet' : 'No bookings found'}
              </h3>
              <p className="text-gray-300 mb-6">
                {bookings?.length === 0
                  ? 'Start planning your next adventure!'
                  : 'Try adjusting your search or filters'
                }
              </p>
              {bookings?.length === 0 ? (
                <a
                  href="/destinations"
                  className="btn-gradient px-6 py-3 rounded-lg inline-flex items-center gap-2"
                >
                  <MapPin className="w-4 h-4" />
                  Explore Destinations
                </a>
              ) : (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedStatus('all');
                  }}
                  className="btn-gradient px-6 py-3 rounded-lg"
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {filteredBookings.map((booking, index) => (
                <motion.div
                  key={booking.booking_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="glass rounded-2xl overflow-hidden hover:shadow-glow transition-all duration-300"
                >
                  <div className="flex flex-col lg:flex-row">
                    {/* Destination Image */}
                    <div className="lg:w-64 h-48 lg:h-auto relative overflow-hidden">
                      <img
                        src={booking.destination_details?.images?.[0] || '/api/placeholder/400/300'}
                        alt={booking.destination_name}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute top-4 left-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(booking.status)}`}>
                          {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                        </span>
                      </div>
                    </div>

                    {/* Booking Details */}
                    <div className="flex-1 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-white mb-1">
                            {booking.destination_name}
                          </h3>
                          <div className="flex items-center gap-2 text-gray-300 text-sm">
                            <MapPin className="w-4 h-4" />
                            <span>
                              {booking.destination_details?.city}, {booking.destination_details?.country}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {getStatusIcon(booking.status)}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-primary-400" />
                          <div>
                            <p className="text-gray-400 text-xs">Check-in</p>
                            <p className="text-white text-sm">
                              {new Date(booking.check_in_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-primary-400" />
                          <div>
                            <p className="text-gray-400 text-xs">Check-out</p>
                            <p className="text-white text-sm">
                              {new Date(booking.check_out_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4 text-primary-400" />
                          <div>
                            <p className="text-gray-400 text-xs">Guests</p>
                            <p className="text-white text-sm">{booking.guests} guest{booking.guests > 1 ? 's' : ''}</p>
                          </div>
                        </div>
                      </div>

                      {booking.special_requests && (
                        <div className="mb-4">
                          <p className="text-gray-400 text-xs mb-1">Special Requests</p>
                          <p className="text-gray-300 text-sm">{booking.special_requests}</p>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <CreditCard className="w-4 h-4 text-green-400" />
                          <span className="text-green-400 font-semibold">
                            ${booking.total_amount || 'TBD'}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setSelectedBooking(booking)}
                            className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors"
                            title="View details"
                          >
                            <Eye className="w-4 h-4 text-white" />
                          </button>

                          {booking.status === 'pending' && (
                            <>
                              <button
                                className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors"
                                title="Edit booking"
                              >
                                <Edit className="w-4 h-4 text-white" />
                              </button>

                              <button
                                onClick={() => handleCancelBooking(booking)}
                                className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center hover:bg-red-700 transition-colors"
                                title="Cancel booking"
                              >
                                <Trash2 className="w-4 h-4 text-white" />
                              </button>
                            </>
                          )}



                          {booking.status === 'completed' && (
                            <button
                              onClick={() => handleOpenReview(booking)}
                              className="w-8 h-8 bg-yellow-600 rounded-full flex items-center justify-center hover:bg-yellow-700 transition-colors"
                              title="Leave review"
                            >
                              <Star className="w-4 h-4 text-white" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Booking Details Modal */}
        <AnimatePresence>
          {selectedBooking && !showCancelModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
              onClick={() => setSelectedBooking(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="glass rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-white">Booking Details</h2>
                  <button
                    onClick={() => setSelectedBooking(null)}
                    className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors"
                  >
                    <XCircle className="w-4 h-4 text-white" />
                  </button>
                </div>

                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Destination</h3>
                      <p className="text-gray-300">{selectedBooking.destination_name}</p>
                      <p className="text-gray-400 text-sm">
                        {selectedBooking.destination_details?.city}, {selectedBooking.destination_details?.country}
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Status</h3>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(selectedBooking.status)}
                        <span className="text-white capitalize">{selectedBooking.status}</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Check-in</h3>
                      <p className="text-gray-300">
                        {new Date(selectedBooking.check_in_date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Check-out</h3>
                      <p className="text-gray-300">
                        {new Date(selectedBooking.check_out_date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Guests</h3>
                      <p className="text-gray-300">{selectedBooking.guests} guest{selectedBooking.guests > 1 ? 's' : ''}</p>
                    </div>
                  </div>

                  {selectedBooking.special_requests && (
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-3">Special Requests</h3>
                      <p className="text-gray-300">{selectedBooking.special_requests}</p>
                    </div>
                  )}

                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3">Booking Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-400 text-sm">Booking ID</p>
                        <p className="text-gray-300 font-mono text-sm">{selectedBooking.booking_id}</p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm">Created</p>
                        <p className="text-gray-300 text-sm">
                          {new Date(selectedBooking.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border-t border-gray-700 pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-400 text-sm">Total Amount</p>
                        <p className="text-2xl font-bold text-green-400">
                          ${selectedBooking.total_amount || 'TBD'}
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                          <Phone className="w-4 h-4" />
                          Contact Support
                        </button>

                        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition-colors">
                          <MessageCircle className="w-4 h-4" />
                          Live Chat
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Cancel Booking Modal */}
        <AnimatePresence>
          {showCancelModal && selectedBooking && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
              onClick={() => setShowCancelModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="glass rounded-2xl p-6 max-w-md w-full"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="text-center">
                  <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <XCircle className="w-8 h-8 text-white" />
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2">Cancel Booking</h3>
                  <p className="text-gray-300 mb-6">
                    Are you sure you want to cancel your booking for {selectedBooking.destination_name}?
                    This action cannot be undone.
                  </p>

                  <div className="flex gap-4">
                    <button
                      onClick={() => setShowCancelModal(false)}
                      className="flex-1 px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Keep Booking
                    </button>

                    <button
                      onClick={confirmCancelBooking}
                      disabled={cancelBookingMutation.isLoading}
                      className="flex-1 px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                    >
                      {cancelBookingMutation.isLoading ? 'Cancelling...' : 'Cancel Booking'}
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Review Modal */}
        <AnimatePresence>
          {showReviewModal && selectedBooking && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
              onClick={() => setShowReviewModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="glass rounded-2xl p-6 max-w-md w-full"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold text-white">Rate {selectedBooking.destination_name}</h3>
                  <button onClick={() => setShowReviewModal(false)}><XCircle className="text-white w-6 h-6" /></button>
                </div>

                <div className="mb-4">
                  <label className="text-gray-300 block mb-2">Rating</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button key={star} onClick={() => setReviewRating(star)}>
                        <Star className={`w-8 h-8 ${star <= reviewRating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-500'}`} />
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mb-6">
                  <label className="text-gray-300 block mb-2">Comment</label>
                  <textarea
                    className="w-full bg-gray-800 text-white rounded p-2"
                    rows="4"
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="Tell us about your experience..."
                  />
                </div>

                <button
                  onClick={submitReview}
                  className="w-full bg-primary-600 hover:bg-primary-700 text-white py-2 rounded-lg font-bold"
                >
                  Submit Review
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EnhancedBookings;