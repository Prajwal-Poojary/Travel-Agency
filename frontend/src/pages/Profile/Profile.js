import React from 'react';
import { motion } from 'framer-motion';
import { User, Settings, Heart, MapPin } from 'lucide-react';

const Profile = () => {
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
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">User Profile</h1>
          <p className="text-gray-300 mb-8">Coming Soon - Advanced profile management with preferences and travel history!</p>
        </div>
      </motion.div>
    </div>
  );
};

export default Profile;