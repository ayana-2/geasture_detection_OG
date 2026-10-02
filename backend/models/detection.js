// backend/models/Detection.js
const mongoose = require('mongoose');

const detectionSchema = new mongoose.Schema({
  gesture: {
    type: String,
    required: true,
    enum: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
           'THUMBS_UP', 'THUMBS_DOWN', 'OK', 'PEACE', 'ROCK', 'LOVE', 'POINT']
  },
  confidence: {
    type: Number,
    required: true,
    min: 0,
    max: 1
  },
  area: {
    type: Number,
    required: true
  },
  handCount: {
    type: Number,
    default: 1,
    min: 1,
    max: 2
  },
  handType: {
    type: String,
    enum: ['left', 'right', 'both'],
    default: 'right'
  },
  imagePath: String,
  debugImagePath: String,
  boundingBox: {
    x: Number,
    y: Number,
    width: Number,
    height: Number
  },
  landmarks: [{
    x: Number,
    y: Number,
    z: Number,
    visibility: Number
  }],
  timestamp: {
    type: Date,
    default: Date.now
  },
  sessionId: String,
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  metadata: {
    device: String,
    resolution: String,
    fps: Number,
    processingTime: Number
  }
}, {
  timestamps: true
});

// Indexes for faster queries
detectionSchema.index({ gesture: 1, timestamp: -1 });
detectionSchema.index({ sessionId: 1 });
detectionSchema.index({ userId: 1, timestamp: -1 });

// Virtual for formatted result
detectionSchema.virtual('result').get(function() {
  return {
    gesture: this.gesture,
    confidence: this.confidence,
    area: this.area,
    message: `Detected ${this.gesture} with ${(this.confidence * 100).toFixed(1)}% confidence`
  };
});

module.exports = mongoose.model('Detection', detectionSchema);