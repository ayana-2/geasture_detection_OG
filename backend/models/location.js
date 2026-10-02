// backend/models/Location.js
const mongoose = require('mongoose');

const locationSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Location name is required'],
    trim: true
  },
  address: {
    street: String,
    city: String,
    state: String,
    country: {
      type: String,
      default: 'USA'
    },
    postalCode: String
  },
  coordinates: {
    latitude: {
      type: Number,
      required: [true, 'Latitude is required'],
      min: -90,
      max: 90
    },
    longitude: {
      type: Number,
      required: [true, 'Longitude is required'],
      min: -180,
      max: 180
    }
  },
  type: {
    type: String,
    enum: ['restaurant', 'hotel', 'museum', 'park', 'mall', 'office', 'residential', 'other'],
    default: 'other'
  },
  description: String,
  amenities: [String],
  openingHours: {
    monday: { open: String, close: String },
    tuesday: { open: String, close: String },
    wednesday: { open: String, close: String },
    thursday: { open: String, close: String },
    friday: { open: String, close: String },
    saturday: { open: String, close: String },
    sunday: { open: String, close: String }
  },
  images: [String],
  rating: {
    type: Number,
    min: 0,
    max: 5,
    default: 0
  },
  contact: {
    phone: String,
    email: String,
    website: String
  },
  isActive: {
    type: Boolean,
    default: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }
}, {
  timestamps: true
});

// Geospatial indexing for location queries
locationSchema.index({ coordinates: '2dsphere' });

// Virtual for formatted address
locationSchema.virtual('formattedAddress').get(function() {
  return `${this.address.street}, ${this.address.city}, ${this.address.state} ${this.address.postalCode}`;
});

// Method to check if location is open
locationSchema.methods.isOpenNow = function() {
  const now = new Date();
  const day = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
  const hours = this.openingHours[day];
  
  if (!hours || !hours.open || !hours.close) return false;
  
  const currentTime = now.getHours() * 100 + now.getMinutes();
  const openTime = parseInt(hours.open.replace(':', ''));
  const closeTime = parseInt(hours.close.replace(':', ''));
  
  return currentTime >= openTime && currentTime <= closeTime;
};

module.exports = mongoose.model('Location', locationSchema);