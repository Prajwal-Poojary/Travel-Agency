const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const bookingSchema = new mongoose.Schema({
  booking_id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  user_id: {
    type: String,
    required: true
  },
  destination_id: {
    type: String,
    required: true
  },
  package_id: {
    type: String,
    default: null
  },
  package_name: {
    type: String,
    default: null
  },
  check_in_date: {
    type: Date,
    required: true
  },
  check_out_date: {
    type: Date,
    required: true
  },
  guests: {
    type: Number,
    required: true,
    min: 1,
    max: 20
  },
  total_price: {
    type: Number,
    required: true,
    min: 0
  },
  special_requests: {
    type: String,
    maxlength: 500,
    default: null
  },
  booking_details: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
    default: {}
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'cancelled', 'completed'],
    default: 'pending'
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
bookingSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

// Validation for check-in/check-out dates
bookingSchema.pre('save', function(next) {
  if (this.check_in_date >= this.check_out_date) {
    next(new Error('Check-in date must be before check-out date'));
  }
  next();
});

module.exports = mongoose.model('Booking', bookingSchema);