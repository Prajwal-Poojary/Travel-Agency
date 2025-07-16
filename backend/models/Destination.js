const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const destinationSchema = new mongoose.Schema({
  destination_id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true,
    maxlength: 200
  },
  country: {
    type: String,
    required: true,
    trim: true,
    maxlength: 100
  },
  city: {
    type: String,
    required: true,
    trim: true,
    maxlength: 100
  },
  category: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  description: {
    type: String,
    required: true,
    maxlength: 2000
  },
  price_range: {
    type: String,
    required: true,
    enum: ['$', '$$', '$$$', '$$$$']
  },
  activities: [{
    type: String,
    trim: true,
    maxlength: 100
  }],
  best_time_to_visit: {
    type: String,
    required: true,
    maxlength: 200
  },
  images: [{
    type: String,
    required: true
  }],
  coordinates: {
    latitude: {
      type: Number,
      required: true,
      min: -90,
      max: 90
    },
    longitude: {
      type: Number,
      required: true,
      min: -180,
      max: 180
    }
  },
  rating: {
    type: Number,
    default: 0,
    min: 0,
    max: 5
  },
  virtual_tour_url: {
    type: String,
    default: null
  },
  featured: {
    type: Boolean,
    default: false
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

// Update timestamp on save
destinationSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

// Index for search functionality
destinationSchema.index({ 
  name: 'text', 
  description: 'text', 
  city: 'text', 
  country: 'text' 
});

module.exports = mongoose.model('Destination', destinationSchema);