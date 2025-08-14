const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const virtualTourSchema = new mongoose.Schema({
  tour_id: {
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
  description: {
    type: String,
    required: true,
    maxlength: 1000
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
  tour_type: {
    type: String,
    required: true,
    enum: ['360_video', 'interactive_360', 'drone_360', 'cultural_360'],
    default: '360_video'
  },
  video_url: {
    type: String,
    required: true
  },
  thumbnail: {
    type: String,
    required: true
  },
  duration: {
    type: String,
    required: true,
    default: '5:00'
  },
  featured: {
    type: Boolean,
    default: false
  },
  views: {
    type: Number,
    default: 0
  },
  rating: {
    type: Number,
    default: 0,
    min: 0,
    max: 5
  },
  features: [{
    type: String,
    trim: true,
    maxlength: 100
  }],
  highlights: [{
    time: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true,
      maxlength: 100
    },
    description: {
      type: String,
      required: true,
      maxlength: 200
    }
  }],
  interactive_elements: [{
    time: {
      type: String,
      required: true
    },
    type: {
      type: String,
      enum: ['hotspot', 'info_panel', 'navigation', 'quiz'],
      required: true
    },
    info: {
      type: String,
      required: true,
      maxlength: 200
    }
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
  destination_id: {
    type: String,
    ref: 'Destination'
  },
  tags: [{
    type: String,
    trim: true,
    maxlength: 50
  }],
  language: {
    type: String,
    default: 'English',
    maxlength: 50
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  },
  active: {
    type: Boolean,
    default: true
  }
});

// Update timestamp on save
virtualTourSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

// Index for search functionality
virtualTourSchema.index({ 
  name: 'text', 
  description: 'text', 
  city: 'text', 
  country: 'text',
  tags: 'text'
});

// Index for filtering by tour type
virtualTourSchema.index({ tour_type: 1 });
virtualTourSchema.index({ featured: 1 });
virtualTourSchema.index({ active: 1 });

module.exports = mongoose.model('VirtualTour', virtualTourSchema);