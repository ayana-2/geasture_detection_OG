// backend/routes/gestureRoutes.js
const express = require('express');
const router = express.Router();
const {
  getGestures,
  createGesture
} = require('../controllers/gestureController');

router.get('/', getGestures);
router.post('/', createGesture);

module.exports = router;