// backend/models/Gesture.js
const mongoose = require('mongoose');

const gestureSchema = new mongoose.Schema({
  letter: {
    type: String,
    required: true,
    unique: true,
    uppercase: true
  },
  name: {
    type: String,
    required: true
  },
  description: String,
  meaning: String,
  commonUses: [String],
  difficulty: {
    type: String,
    enum: ['easy', 'medium', 'hard'],
    default: 'medium'
  },
  imageUrl: String,
  landmarksPattern: [{
    x: Number,
    y: Number,
    z: Number
  }],
  accuracy: {
    type: Number,
    default: 0,
    min: 0,
    max: 100
  },
  sampleCount: {
    type: Number,
    default: 0
  },
  isActive: {
    type: Boolean,
    default: true
  },
  category: {
    type: String,
    enum: ['alphabet', 'number', 'symbol', 'custom'],
    default: 'alphabet'
  }
}, {
  timestamps: true
});

// Pre-save hook to ensure uppercase
gestureSchema.pre('save', function(next) {
  this.letter = this.letter.toUpperCase();
  next();
});

module.exports = mongoose.model('Gesture', gestureSchema);