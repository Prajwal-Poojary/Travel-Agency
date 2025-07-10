import React from 'react';
import { motion } from 'framer-motion';
import { Globe, Users, Award, Zap } from 'lucide-react';

const About = () => {
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
            <Globe className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">About TravelAI</h1>
          <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
            We're revolutionizing travel with AI-powered recommendations, virtual tours, and seamless booking experiences. 
            Our platform combines cutting-edge technology with curated travel expertise to create unforgettable journeys.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">50K+ Travelers</h3>
              <p className="text-gray-300 text-sm">Happy customers worldwide</p>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">200+ Destinations</h3>
              <p className="text-gray-300 text-sm">Curated travel experiences</p>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Award className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">4.9/5 Rating</h3>
              <p className="text-gray-300 text-sm">Exceptional service quality</p>
            </div>

            <div className="glass rounded-xl p-6">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">AI Powered</h3>
              <p className="text-gray-300 text-sm">Smart recommendations</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default About;