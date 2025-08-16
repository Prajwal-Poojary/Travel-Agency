import React from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import { Heart, Play, MapPin, Clock, Camera } from 'lucide-react';

const FavoritesVirtualTours = () => {
  const { data, isLoading, error } = useQuery('favorite-virtual-tours', apiService.listFavoriteVirtualTours);
  const items = data?.items || [];

  if (error) {
    return (
      <div className="min-h-screen pt-20 flex items-center justify-center">
        <div className="text-center text-white">Failed to load favorites</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Heart className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-2">My Favorite Tours</h1>
          <p className="text-gray-300">Quick access to the virtual tours you love</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <LoadingSpinner size="large" text="Loading favorites..." />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20">
            <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-2">No favorites yet</h3>
            <p className="text-gray-300">Mark tours as favorites to see them here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((tour, idx) => (
              <motion.div key={tour.tour_id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: idx * 0.05 }} className="glass rounded-xl overflow-hidden">
                <div className="relative h-48 overflow-hidden">
                  <img src={tour.thumbnail} alt={tour.name} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
                  <div className="absolute top-4 left-4 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1"><span className="text-white text-sm font-medium">{tour.country}</span></div>
                  <div className="absolute top-4 right-4 w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center"><Play className="w-5 h-5 text-white ml-1" /></div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-white mb-2">{tour.name}</h3>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <div className="flex items-center gap-1"><Clock className="w-4 h-4" /><span>{tour.duration}</span></div>
                    <div className="flex items-center gap-1"><MapPin className="w-4 h-4" /><span>{tour.country}</span></div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FavoritesVirtualTours;