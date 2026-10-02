// backend/routes/detectionRoutes.js
const express = require('express');
const router = express.Router();
const {
  processDetection,
  getDetections,
  getDetection,
  detectionStream
} = require('../controllers/detectioncontroller');

router.post('/', processDetection);
router.get('/', getDetections);
router.get('/stream', detectionStream);
router.get('/:id', getDetection);

module.exports = router;