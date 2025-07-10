import React from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapPin, Star, Calendar, Users, Camera, Heart, ArrowRight } from 'lucide-react';

const DestinationDetail = () => {
  const { id } = useParams();

  return (
    <div className="min-h-screen pt-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-7xl mx-auto px-4 py-12"
      >
        <div className="glass rounded-2xl p-8 text-center">
          <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <MapPin className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">Destination Details</h1>
          <p className="text-gray-300 mb-8">Coming Soon - Advanced destination details with 360° tours, booking, and more!</p>
          <div className="text-sm text-gray-400">Destination ID: {id}</div>
        </div>
      </motion.div>
    </div>
  );
};

export default DestinationDetail;