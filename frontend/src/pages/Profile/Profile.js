import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Settings, Mail, Calendar, Edit3, MapPin, Check, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || ''
  });
  const [isSaving, setIsSaving] = useState(false);

  const handleEdit = () => {
    setFormData({
      full_name: user?.full_name || '',
      email: user?.email || ''
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    const res = await updateProfile(formData);
    if (res.success) {
      setIsEditing(false);
    }
    setIsSaving(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen pt-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-4xl mx-auto px-4 py-12"
      >
        <div className="glass rounded-2xl p-8 mb-8">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="w-32 h-32 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center shadow-glow">
              <User className="w-16 h-16 text-white" />
            </div>

            <div className="text-center md:text-left flex-1">
              <h1 className="text-4xl font-bold text-white mb-2">{user?.username || 'Traveler'}</h1>
              <p className="text-gray-300 flex items-center justify-center md:justify-start gap-2 mb-4">
                <MapPin className="w-4 h-4" /> Earth Explorer
              </p>
            </div>

            {!isEditing ? (
              <button onClick={handleEdit} className="btn-gradient px-6 py-3 rounded-lg flex items-center gap-2">
                <Edit3 className="w-4 h-4" /> Edit Profile
              </button>
            ) : (
              <div className="flex gap-2">
                <button onClick={handleSave} disabled={isSaving} className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-colors">
                  <Check className="w-4 h-4" /> {isSaving ? 'Saving...' : 'Save'}
                </button>
                <button onClick={() => setIsEditing(false)} disabled={isSaving} className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg flex items-center gap-2 transition-colors">
                  <X className="w-4 h-4" /> Cancel
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Account Details */}
          <div className="glass rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Settings className="w-6 h-6 text-primary-400" /> Account Details
            </h3>

            <div className="space-y-6">
              <div>
                <label className="text-gray-400 text-sm">Full Name</label>
                {isEditing ? (
                  <input type="text" name="full_name" value={formData.full_name} onChange={handleChange} className="w-full mt-1 p-2 rounded-lg bg-gray-800 text-white border border-gray-700 focus:border-primary-500 focus:outline-none" />
                ) : (
                  <div className="text-white text-lg font-medium">{user?.full_name || 'Not provided'}</div>
                )}
              </div>

              <div>
                <label className="text-gray-400 text-sm">Email Address</label>
                {isEditing ? (
                  <input type="email" name="email" value={formData.email} onChange={handleChange} className="w-full mt-1 p-2 rounded-lg bg-gray-800 text-white border border-gray-700 focus:border-primary-500 focus:outline-none" />
                ) : (
                  <div className="text-white text-lg font-medium flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    {user?.email || 'No email found'}
                  </div>
                )}
              </div>

              <div>
                <label className="text-gray-400 text-sm">Member Since</label>
                <div className="text-white text-lg font-medium flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Recently'}
                </div>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="glass rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <User className="w-6 h-6 text-primary-400" /> Preferences
            </h3>

            <div className="space-y-4">
              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="text-white font-medium mb-1">Travel Style</div>
                <div className="text-gray-400 text-sm">Adventure & Culture</div>
              </div>

              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="text-white font-medium mb-1">Preferred Destinations</div>
                <div className="text-gray-400 text-sm">Europe, Asia</div>
              </div>

              <div className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="text-white font-medium mb-1">Email Notifications</div>
                <div className="text-gray-400 text-sm">Enabled for new bookings and recommendations</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Profile;