import React from 'react';
import { motion } from 'framer-motion';
import { Camera, Play, Globe, Headphones } from 'lucide-react';

const VirtualTours = () => {
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
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">Virtual Tours</h1>
          <p className="text-gray-300 mb-8">Coming Soon - Immersive 360° virtual tours of destinations!</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Play className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">360° Videos</h3>
              <p className="text-gray-300 text-sm">Immersive video experiences</p>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">VR Ready</h3>
              <p className="text-gray-300 text-sm">Virtual reality compatibility</p>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Headphones className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Audio Guide</h3>
              <p className="text-gray-300 text-sm">Professional narration</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default VirtualTours;