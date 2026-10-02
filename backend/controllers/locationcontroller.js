// backend/controllers/locationController.js
const Location = require('../models/location');

// @desc    Get all locations
// @route   GET /api/locations
// @access  Public
exports.getLocations = async (req, res) => {
  try {
    const {
      type,
      city,
      minRating,
      isOpen,
      page = 1,
      limit = 10,
      sortBy = 'name',
      sortOrder = 'asc',
      search,
      coordinates,
      radius = 5000 // in meters
    } = req.query;

    let query = { isActive: true };

    // Filter by type
    if (type) {
      query.type = type;
    }

    // Filter by city
    if (city) {
      query['address.city'] = new RegExp(city, 'i');
    }

    // Filter by minimum rating
    if (minRating) {
      query.rating = { $gte: parseFloat(minRating) };
    }

    // Search by name or description
    if (search) {
      query.$or = [
        { name: new RegExp(search, 'i') },
        { description: new RegExp(search, 'i') },
        { 'address.city': new RegExp(search, 'i') }
      ];
    }

    // Geospatial query - find locations within radius
    if (coordinates) {
      const [lng, lat] = coordinates.split(',').map(Number);
      if (lng && lat) {
        query.coordinates = {
          $near: {
            $geometry: {
              type: "Point",
              coordinates: [lng, lat]
            },
            $maxDistance: parseInt(radius)
          }
        };
      }
    }

    // Sorting
    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;

    // Pagination
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;

    const locations = await Location.find(query)
      .sort(sort)
      .limit(limit)
      .skip(startIndex)
      .populate('createdBy', 'name email');

    // Get total count for pagination info
    const total = await Location.countDocuments(query);

    // Pagination result
    const pagination = {};
    
    if (endIndex < total) {
      pagination.next = {
        page: parseInt(page) + 1,
        limit: parseInt(limit)
      };
    }
    
    if (startIndex > 0) {
      pagination.prev = {
        page: parseInt(page) - 1,
        limit: parseInt(limit)
      };
    }

    res.status(200).json({
      success: true,
      count: locations.length,
      pagination,
      total,
      data: locations
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Get single location
// @route   GET /api/locations/:id
// @access  Public
exports.getLocation = async (req, res) => {
  try {
    const location = await Location.findById(req.params.id)
      .populate('createdBy', 'name email');

    if (!location) {
      return res.status(404).json({
        success: false,
        message: 'Location not found'
      });
    }

    res.status(200).json({
      success: true,
      data: location
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Create location
// @route   POST /api/locations
// @access  Private
exports.createLocation = async (req, res) => {
  try {
    // Add user to request body
    req.body.createdBy = req.user.id;

    const location = await Location.create(req.body);

    res.status(201).json({
      success: true,
      data: location
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: 'Error creating location',
      error: error.message
    });
  }
};

// @desc    Update location
// @route   PUT /api/locations/:id
// @access  Private
exports.updateLocation = async (req, res) => {
  try {
    let location = await Location.findById(req.params.id);

    if (!location) {
      return res.status(404).json({
        success: false,
        message: 'Location not found'
      });
    }

    // Make sure user is location owner or admin
    if (location.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to update this location'
      });
    }

    location = await Location.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });

    res.status(200).json({
      success: true,
      data: location
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: 'Error updating location',
      error: error.message
    });
  }
};

// @desc    Delete location
// @route   DELETE /api/locations/:id
// @access  Private
exports.deleteLocation = async (req, res) => {
  try {
    const location = await Location.findById(req.params.id);

    if (!location) {
      return res.status(404).json({
        success: false,
        message: 'Location not found'
      });
    }

    // Make sure user is location owner or admin
    if (location.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to delete this location'
      });
    }

    await location.deleteOne();

    res.status(200).json({
      success: true,
      message: 'Location deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Get locations within radius
// @route   GET /api/locations/radius/:zipcode/:distance
// @access  Public
exports.getLocationsInRadius = async (req, res) => {
  try {
    const { zipcode, distance } = req.params;

    // Get lat/lng from zipcode (you'll need a geocoding service)
    // For now, using coordinates directly
    const { lat, lng } = req.query;

    // Calc radius using radians
    // Divide distance by radius of Earth (3,963 mi / 6,378 km)
    const radius = distance / 3963;

    const locations = await Location.find({
      coordinates: {
        $geoWithin: { $centerSphere: [[lng, lat], radius] }
      }
    });

    res.status(200).json({
      success: true,
      count: locations.length,
      data: locations
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};

// @desc    Upload location photo
// @route   PUT /api/locations/:id/photo
// @access  Private
exports.uploadLocationPhoto = async (req, res) => {
  try {
    const location = await Location.findById(req.params.id);

    if (!location) {
      return res.status(404).json({
        success: false,
        message: 'Location not found'
      });
    }

    // Check ownership
    if (location.createdBy.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to update this location'
      });
    }

    if (!req.files) {
      return res.status(400).json({
        success: false,
        message: 'Please upload a file'
      });
    }

    const file = req.files.file;

    // Check if image
    if (!file.mimetype.startsWith('image')) {
      return res.status(400).json({
        success: false,
        message: 'Please upload an image file'
      });
    }

    // Check file size
    if (file.size > process.env.MAX_FILE_UPLOAD) {
      return res.status(400).json({
        success: false,
        message: `Please upload an image less than ${process.env.MAX_FILE_UPLOAD}`
      });
    }

    // Create custom filename
    file.name = `photo_${location._id}${path.parse(file.name).ext}`;

    // Upload file
    file.mv(`${process.env.FILE_UPLOAD_PATH}/${file.name}`, async err => {
      if (err) {
        console.error(err);
        return res.status(500).json({
          success: false,
          message: 'Problem with file upload'
        });
      }

      await Location.findByIdAndUpdate(req.params.id, {
        $push: { images: file.name }
      });

      res.status(200).json({
        success: true,
        data: file.name
      });
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error',
      error: error.message
    });
  }
};