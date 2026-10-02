// backend/controllers/detectionController.js
const Detection = require('../models/detection');
const Gesture = require('../models/gesture');
const path = require('path');
const fs = require('fs');

// @desc    Process hand detection
// @route   POST /api/detect
// @access  Public
exports.processDetection = async (req, res) => {
  try {
    const { gesture, confidence, area, handCount = 1, handType = 'right', landmarks, sessionId, metadata } = req.body;
    
    // Validate required fields
    if (!gesture || confidence === undefined) {
      return res.status(400).json({
        success: false,
        error: 'Gesture and confidence are required'
      });
    }

    // Check if gesture exists in dictionary
    const gestureExists = await Gesture.findOne({ letter: gesture.toUpperCase() });
    if (!gestureExists && !gesture.startsWith('CUSTOM_')) {
      console.log(`⚠️ Unknown gesture detected: ${gesture}`);
      // Still save it, but mark as unknown
    }

    // Handle file upload if present
    let imagePath = null;
    let debugImagePath = null;

    if (req.files && req.files.image) {
      const image = req.files.image;
      const fileName = `detection_${Date.now()}_${Math.random().toString(36).substr(2, 9)}${path.extname(image.name)}`;
      imagePath = path.join('uploads', fileName);
      await image.mv(imagePath);
    }

    if (req.files && req.files.debugImage) {
      const debugImage = req.files.debugImage;
      const debugFileName = `debug_${Date.now()}_${Math.random().toString(36).substr(2, 9)}${path.extname(debugImage.name)}`;
      debugImagePath = path.join('debug_frames', debugFileName);
      await debugImage.mv(debugImagePath);
    }

    // Create detection record
    const detection = await Detection.create({
      gesture: gesture.toUpperCase(),
      confidence: parseFloat(confidence),
      area: parseFloat(area || 0),
      handCount: parseInt(handCount),
      handType,
      landmarks: landmarks || [],
      sessionId: sessionId || req.ip,
      userId: req.user?.id,
      imagePath,
      debugImagePath,
      metadata: {
        device: metadata?.device || req.headers['user-agent'],
        resolution: metadata?.resolution,
        fps: metadata?.fps,
        processingTime: metadata?.processingTime,
        ip: req.ip
      }
    });

    // Update gesture accuracy stats
    if (gestureExists) {
      const recentDetections = await Detection.find({
        gesture: gesture.toUpperCase(),
        confidence: { $gte: 0.7 }
      }).limit(100);

      const avgConfidence = recentDetections.length > 0
        ? recentDetections.reduce((sum, d) => sum + d.confidence, 0) / recentDetections.length
        : 0;

      await Gesture.updateOne(
        { letter: gesture.toUpperCase() },
        {
          $inc: { sampleCount: 1 },
          $set: { accuracy: Math.round(avgConfidence * 100) }
        }
      );
    }

    // Log to console
    console.log(`✅ Hand detected: ${detection.gesture} (Area: ${detection.area}, Confidence: ${detection.confidence.toFixed(2)})`);
    
    if (debugImagePath) {
      console.log(`📸 Saved debug image: ${debugImagePath}`);
    }

    res.status(200).json({
      success: true,
      message: `🎯 Detection result: ${detection.gesture} (${detection.confidence.toFixed(2)})`,
      data: {
        detection: detection.result,
        id: detection._id,
        timestamp: detection.timestamp,
        imageUrl: imagePath ? `/${imagePath}` : null,
        debugImageUrl: debugImagePath ? `/${debugImagePath}` : null
      }
    });

  } catch (error) {
    console.error('❌ Detection error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process detection',
      message: error.message
    });
  }
};

// @desc    Get detection history
// @route   GET /api/detect
// @access  Public
exports.getDetections = async (req, res) => {
  try {
    const { 
      limit = 50, 
      page = 1, 
      gesture, 
      minConfidence = 0.5,
      startDate,
      endDate,
      sessionId 
    } = req.query;

    const query = {};

    if (gesture) {
      query.gesture = gesture.toUpperCase();
    }

    if (minConfidence) {
      query.confidence = { $gte: parseFloat(minConfidence) };
    }

    if (sessionId) {
      query.sessionId = sessionId;
    }

    if (startDate || endDate) {
      query.timestamp = {};
      if (startDate) query.timestamp.$gte = new Date(startDate);
      if (endDate) query.timestamp.$lte = new Date(endDate);
    }

    const skip = (page - 1) * limit;

    const detections = await Detection.find(query)
      .sort({ timestamp: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .lean();

    const total = await Detection.countDocuments(query);

    // Get statistics
    const stats = await Detection.aggregate([
      { $match: query },
      {
        $group: {
          _id: '$gesture',
          count: { $sum: 1 },
          avgConfidence: { $avg: '$confidence' },
          avgArea: { $avg: '$area' }
        }
      },
      { $sort: { count: -1 } }
    ]);

    res.status(200).json({
      success: true,
      count: detections.length,
      total,
      page: parseInt(page),
      pages: Math.ceil(total / limit),
      data: detections,
      statistics: stats
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch detections'
    });
  }
};

// @desc    Get detection by ID
// @route   GET /api/detect/:id
// @access  Public
exports.getDetection = async (req, res) => {
  try {
    const detection = await Detection.findById(req.params.id);

    if (!detection) {
      return res.status(404).json({
        success: false,
        error: 'Detection not found'
      });
    }

    res.status(200).json({
      success: true,
      data: detection
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch detection'
    });
  }
};

// @desc    Get real-time detection stream (SSE)
// @route   GET /api/detect/stream
// @access  Public
exports.detectionStream = async (req, res) => {
  try {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    console.log('🔗 Client connected to detection stream');

    // Send initial connection message
    res.write('event: connected\n');
    res.write(`data: ${JSON.stringify({ message: 'Connected to detection stream', timestamp: new Date().toISOString() })}\n\n`);

    // Watch for new detections
    const changeStream = Detection.watch();

    changeStream.on('change', (change) => {
      if (change.operationType === 'insert') {
        const detection = change.fullDocument;
        res.write('event: detection\n');
        res.write(`data: ${JSON.stringify({
          gesture: detection.gesture,
          confidence: detection.confidence,
          timestamp: detection.timestamp,
          id: detection._id
        })}\n\n`);
      }
    });

    // Handle client disconnect
    req.on('close', () => {
      console.log('🔌 Client disconnected from detection stream');
      changeStream.close();
      res.end();
    });

  } catch (error) {
    console.error('❌ Stream error:', error);
    res.status(500).json({
      success: false,
      error: 'Stream error'
    });
  }
};