const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

const chatSessionSchema = new mongoose.Schema({
  session_id: {
    type: String,
    default: uuidv4,
    unique: true,
    required: true
  },
  user_id: {
    type: String,
    default: null
  },
  messages: [{
    role: {
      type: String,
      enum: ['user', 'assistant'],
      required: true
    },
    content: {
      type: String,
      required: true
    },
    timestamp: {
      type: Date,
      default: Date.now
    }
  }],
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
chatSessionSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

module.exports = mongoose.model('ChatSession', chatSessionSchema);