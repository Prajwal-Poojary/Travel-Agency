const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const travelPackageSchema = new mongoose.Schema({
  package_id: {
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
    maxlength: 2000
  },
  destinations: [{
    type: String,
    required: true
  }],
  duration: {
    type: String,
    required: true,
    maxlength: 50
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  original_price: {
    type: Number,
    default: null,
    min: 0
  },
  savings: {
    type: Number,
    default: null,
    min: 0
  },
  includes: [{
    type: String,
    trim: true,
    maxlength: 200
  }],
  image: {
    type: String,
    required: true
  },
  featured: {
    type: Boolean,
    default: false
  },
  available: {
    type: Boolean,
    default: true
  },
  max_group_size: {
    type: Number,
    default: 4,
    min: 1,
    max: 50
  },
  difficulty: {
    type: String,
    enum: ['Easy', 'Moderate', 'Hard', 'Expert'],
    default: 'Moderate'
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
travelPackageSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

module.exports = mongoose.model('TravelPackage', travelPackageSchema);