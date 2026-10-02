// backend/routes/locationRoutes.js
const express = require('express');
const router = express.Router();
const {
  getLocations,
  getLocation,
  createLocation,
  updateLocation,
  deleteLocation,
  getLocationsInRadius,
  uploadLocationPhoto
} = require('../controllers/locationcontroller');

// Protect middleware
const { protect, authorize } = require('../middleware/auth');

router
  .route('/')
  .get(getLocations)
  .post(protect, authorize('admin', 'user'), createLocation);

router
  .route('/radius/:zipcode/:distance')
  .get(getLocationsInRadius);

router
  .route('/:id')
  .get(getLocation)
  .put(protect, authorize('admin', 'user'), updateLocation)
  .delete(protect, authorize('admin', 'user'), deleteLocation);

router
  .route('/:id/photo')
  .put(protect, authorize('admin', 'user'), uploadLocationPhoto);

module.exports = router;