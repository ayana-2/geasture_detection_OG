// backend/controllers/gestureController.js
const Gesture = require('../models/gesture');
const Detection = require('../models/detection');

// @desc    Get all gestures
// @route   GET /api/gestures
// @access  Public
exports.getGestures = async (req, res) => {
  try {
    const gestures = await Gesture.find({ isActive: true })
      .sort({ letter: 1 })
      .lean();

    // Get statistics for each gesture
    const gesturesWithStats = await Promise.all(
      gestures.map(async (gesture) => {
        const stats = await Detection.aggregate([
          { $match: { gesture: gesture.letter, confidence: { $gte: 0.5 } } },
          {
            $group: {
              _id: null,
              totalDetections: { $sum: 1 },
              avgConfidence: { $avg: '$confidence' },
              lastDetection: { $max: '$timestamp' }
            }
          }
        ]);

        return {
          ...gesture,
          stats: stats[0] || {
            totalDetections: 0,
            avgConfidence: 0,
            lastDetection: null
          }
        };
      })
    );

    res.status(200).json({
      success: true,
      count: gesturesWithStats.length,
      data: gesturesWithStats
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch gestures'
    });
  }
};

// @desc    Create/update gesture
// @route   POST /api/gestures
// @access  Private (Admin)
exports.createGesture = async (req, res) => {
  try {
    const { letter, name, description, meaning, difficulty, imageUrl } = req.body;

    // Check if gesture exists
    let gesture = await Gesture.findOne({ letter: letter.toUpperCase() });

    if (gesture) {
      // Update existing gesture
      gesture = await Gesture.findOneAndUpdate(
        { letter: letter.toUpperCase() },
        { name, description, meaning, difficulty, imageUrl },
        { new: true, runValidators: true }
      );
    } else {
      // Create new gesture
      gesture = await Gesture.create({
        letter: letter.toUpperCase(),
        name,
        description,
        meaning,
        difficulty,
        imageUrl
      });
    }

    res.status(200).json({
      success: true,
      message: `Gesture ${gesture.letter} ${gesture ? 'updated' : 'created'} successfully`,
      data: gesture
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: 'Failed to save gesture',
      message: error.message
    });
  }
};