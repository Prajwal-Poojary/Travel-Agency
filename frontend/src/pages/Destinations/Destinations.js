import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  MapPin, 
  Star, 
  Calendar, 
  DollarSign,
  Grid,
  List,
  ArrowRight,
  Heart,
  Camera,
  Clock
} from 'lucide-react';
import { useQuery } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const Destinations = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    country: '',
    minPrice: '',
    maxPrice: '',
    activity: '',
    rating: ''
  });
  const [viewMode, setViewMode] = useState('grid');
  const [showFilters, setShowFilters] = useState(false);

  // Fetch destinations with filters
  const { data: destinations, isLoading, error } = useQuery(
    ['destinations', searchTerm, filters],
    () => apiService.getDestinations({
      search: searchTerm || undefined,
      country: filters.country || undefined,
      min_price: filters.minPrice || undefined,
      max_price: filters.maxPrice || undefined,
      activity: filters.activity || undefined,
    }),
    {
      enabled: true,
      staleTime: 5 * 60 * 1000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching destinations:', error);
        toast.error('Failed to load destinations');
      }
    }
  );

  const handleSearch = (e) => {
    e.preventDefault();
    // Search is handled by the query refetch
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      country: '',
      minPrice: '',
      maxPrice: '',
      activity: '',
      rating: ''
    });
    setSearchTerm('');
  };

  const countries = ['Japan', 'Switzerland', 'Maldives', 'Greece', 'UAE', 'Indonesia', 'Iceland', 'Peru'];
  const activities = ['Skiing', 'Snorkeling', 'Spa', 'Hiking', 'Cultural Tours', 'Photography', 'Adventure Sports'];

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Error Loading Destinations</h2>
          <p className="text-gray-300 mb-6">Please try again later</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn-gradient px-6 py-3 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20">
      {/* Header */}
      <section className="py-12 px-4 bg-gradient-to-r from-primary-900/20 to-secondary-900/20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-gradient">
              Discover Amazing Destinations
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Explore the world's most beautiful places with our curated selection of premium destinations
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            onSubmit={handleSearch}
            className="max-w-2xl mx-auto"
          >
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search destinations, countries, or activities..."
                className="input-futuristic w-full pl-12 pr-4 py-4 rounded-full text-lg"
              />
            </div>
          </motion.form>
        </div>
      </section>

      {/* Filters and Controls */}
      <section className="py-6 px-4 bg-black/20">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Filter Toggle */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="glass px-4 py-2 rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2"
              >
                <Filter className="w-4 h-4" />
                Filters
              </button>
              
              {(searchTerm || Object.values(filters).some(v => v)) && (
                <button
                  onClick={clearFilters}
                  className="text-primary-400 hover:text-primary-300 text-sm"
                >
                  Clear All
                </button>
              )}
            </div>

            {/* Results Count and View Mode */}
            <div className="flex items-center gap-4">
              <span className="text-gray-300 text-sm">
                {destinations?.length || 0} destinations found
              </span>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'grid' ? 'bg-primary-500 text-white' : 'glass hover:bg-white/10'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'list' ? 'bg-primary-500 text-white' : 'glass hover:bg-white/10'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 glass rounded-lg p-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Country Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Country</label>
                  <select
                    value={filters.country}
                    onChange={(e) => handleFilterChange('country', e.target.value)}
                    className="input-futuristic w-full px-3 py-2 rounded-lg"
                  >
                    <option value="">All Countries</option>
                    {countries.map(country => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>

                {/* Activity Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Activity</label>
                  <select
                    value={filters.activity}
                    onChange={(e) => handleFilterChange('activity', e.target.value)}
                    className="input-futuristic w-full px-3 py-2 rounded-lg"
                  >
                    <option value="">All Activities</option>
                    {activities.map(activity => (
                      <option key={activity} value={activity}>{activity}</option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Min Price</label>
                  <input
                    type="number"
                    value={filters.minPrice}
                    onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                    placeholder="Min price"
                    className="input-futuristic w-full px-3 py-2 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Max Price</label>
                  <input
                    type="number"
                    value={filters.maxPrice}
                    onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                    placeholder="Max price"
                    className="input-futuristic w-full px-3 py-2 rounded-lg"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* Results */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          {isLoading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner size="large" text="Loading destinations..." />
            </div>
          ) : destinations?.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">No destinations found</h3>
              <p className="text-gray-300 mb-6">Try adjusting your search or filters</p>
              <button
                onClick={clearFilters}
                className="btn-gradient px-6 py-3 rounded-lg"
              >
                Clear Filters
              </button>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className={
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8'
                  : 'space-y-6'
              }
            >
              {destinations?.map((destination, index) => (
                <motion.div
                  key={destination.destination_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className={`glass rounded-2xl overflow-hidden hover:shadow-glow transition-all duration-300 group ${
                    viewMode === 'list' ? 'flex flex-col md:flex-row' : ''
                  }`}
                >
                  {/* Image */}
                  <div className={`relative overflow-hidden ${
                    viewMode === 'list' ? 'md:w-1/3 h-64 md:h-auto' : 'h-64'
                  }`}>
                    <img
                      src={destination.images?.[0] || '/api/placeholder/400/300'}
                      alt={destination.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                    
                    {/* Overlay Info */}
                    <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
                      <div className="bg-black/50 backdrop-blur-sm rounded-full px-3 py-1">
                        <span className="text-white text-sm font-medium">{destination.country}</span>
                      </div>
                      <button className="w-8 h-8 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-black/70 transition-colors">
                        <Heart className="w-4 h-4 text-white" />
                      </button>
                    </div>

                    <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
                      <div className="bg-black/50 backdrop-blur-sm rounded-full px-2 py-1 flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        <span className="text-white text-sm">{destination.rating}</span>
                      </div>
                      <button className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors">
                        <Camera className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* Content */}
                  <div className={`p-6 ${viewMode === 'list' ? 'md:w-2/3 flex flex-col justify-between' : ''}`}>
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{destination.name}</h3>
                      <p className="text-gray-300 mb-4 line-clamp-3">{destination.description}</p>
                      
                      {/* Activities */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {destination.activities?.slice(0, 3).map((activity, i) => (
                          <span
                            key={i}
                            className="bg-primary-500/20 text-primary-300 px-2 py-1 rounded-full text-xs"
                          >
                            {activity}
                          </span>
                        ))}
                        {destination.activities?.length > 3 && (
                          <span className="text-gray-400 text-xs">+{destination.activities.length - 3} more</span>
                        )}
                      </div>

                      {/* Best Time */}
                      <div className="flex items-center gap-2 mb-4 text-gray-400 text-sm">
                        <Clock className="w-4 h-4" />
                        <span>Best time: {destination.best_time_to_visit}</span>
                      </div>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-green-400" />
                        <span className="text-green-400 font-semibold text-sm">
                          {destination.price_range}
                        </span>
                      </div>
                      
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
            </motion.div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Destinations;