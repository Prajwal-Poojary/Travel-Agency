const express = require('express');
const { body, validationResult } = require('express-validator');
const TravelPackage = require('../models/TravelPackage');
const Destination = require('../models/Destination');
const Booking = require('../models/Booking');
const auth = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/packages
// @desc    Get travel packages
// @access  Public
router.get('/', async (req, res) => {
  try {
    const { featured_only } = req.query;
    
    let query = {};
    if (featured_only === 'true') {
      query.featured = true;
    }
    
    const packages = await TravelPackage.find(query)
      .sort({ featured: -1, created_at: -1 })
      .limit(50);
    
    res.json(packages);
  } catch (error) {
    console.error('Get packages error:', error);
    res.status(500).json({ error: 'Server error fetching packages' });
  }
});

// @route   GET /api/packages/:package_id
// @desc    Get specific travel package
// @access  Public
router.get('/:package_id', async (req, res) => {
  try {
    const { package_id } = req.params;
    
    const package = await TravelPackage.findOne({ package_id });
    
    if (!package) {
      return res.status(404).json({ error: 'Package not found' });
    }
    
    // Get destination details for the package
    const destinationDetails = await Promise.all(
      package.destinations.map(async (destName) => {
        const destination = await Destination.findOne({ name: destName });
        return destination ? {
          destination_id: destination.destination_id,
          name: destination.name,
          city: destination.city,
          country: destination.country,
          description: destination.description,
          images: destination.images,
          activities: destination.activities,
          coordinates: destination.coordinates
        } : null;
      })
    );
    
    res.json({
      ...package.toObject(),
      destination_details: destinationDetails.filter(dest => dest !== null)
    });
  } catch (error) {
    console.error('Get package error:', error);
    res.status(500).json({ error: 'Server error fetching package' });
  }
});

// @route   POST /api/packages
// @desc    Create travel package
// @access  Private (Admin)
router.post('/', auth, [
  body('name').isLength({ min: 1, max: 200 }).trim(),
  body('description').isLength({ min: 1, max: 2000 }),
  body('destinations').isArray().notEmpty(),
  body('duration').isLength({ min: 1, max: 50 }),
  body('price').isFloat({ min: 0 }),
  body('includes').isArray(),
  body('image').isURL(),
  body('max_group_size').optional().isInt({ min: 1, max: 50 }),
  body('difficulty').optional().isIn(['Easy', 'Moderate', 'Hard', 'Expert'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const packageData = req.body;
    
    // Calculate savings if original_price is provided
    if (packageData.original_price && packageData.original_price > packageData.price) {
      packageData.savings = packageData.original_price - packageData.price;
    }
    
    const travelPackage = new TravelPackage(packageData);
    await travelPackage.save();
    
    res.status(201).json(travelPackage);
  } catch (error) {
    console.error('Create package error:', error);
    res.status(500).json({ error: 'Server error creating package' });
  }
});

// @route   PUT /api/packages/:package_id
// @desc    Update travel package
// @access  Private (Admin)
router.put('/:package_id', auth, [
  body('name').optional().isLength({ min: 1, max: 200 }).trim(),
  body('description').optional().isLength({ min: 1, max: 2000 }),
  body('destinations').optional().isArray().notEmpty(),
  body('duration').optional().isLength({ min: 1, max: 50 }),
  body('price').optional().isFloat({ min: 0 }),
  body('includes').optional().isArray(),
  body('image').optional().isURL(),
  body('featured').optional().isBoolean(),
  body('available').optional().isBoolean(),
  body('max_group_size').optional().isInt({ min: 1, max: 50 }),
  body('difficulty').optional().isIn(['Easy', 'Moderate', 'Hard', 'Expert'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { package_id } = req.params;
    const updates = req.body;
    
    const travelPackage = await TravelPackage.findOne({ package_id });
    
    if (!travelPackage) {
      return res.status(404).json({ error: 'Package not found' });
    }
    
    // Update package fields
    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        travelPackage[key] = updates[key];
      }
    });
    
    // Recalculate savings if prices changed
    if (travelPackage.original_price && travelPackage.original_price > travelPackage.price) {
      travelPackage.savings = travelPackage.original_price - travelPackage.price;
    }
    
    await travelPackage.save();
    
    res.json(travelPackage);
  } catch (error) {
    console.error('Update package error:', error);
    res.status(500).json({ error: 'Server error updating package' });
  }
});

// @route   DELETE /api/packages/:package_id
// @desc    Delete travel package
// @access  Private (Admin)
router.delete('/:package_id', auth, async (req, res) => {
  try {
    const { package_id } = req.params;
    
    const travelPackage = await TravelPackage.findOne({ package_id });
    
    if (!travelPackage) {
      return res.status(404).json({ error: 'Package not found' });
    }
    
    await TravelPackage.findOneAndDelete({ package_id });
    
    res.json({ message: 'Package deleted successfully' });
  } catch (error) {
    console.error('Delete package error:', error);
    res.status(500).json({ error: 'Server error deleting package' });
  }
});

// @route   POST /api/packages/:package_id/book
// @desc    Book a travel package
// @access  Private
router.post('/:package_id/book', auth, [
  body('booking_details').isObject(),
  body('check_in_date').isISO8601(),
  body('check_out_date').isISO8601(),
  body('guests').isInt({ min: 1, max: 20 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { package_id } = req.params;
    const { booking_details, check_in_date, check_out_date, guests } = req.body;
    
    const travelPackage = await TravelPackage.findOne({ package_id });
    
    if (!travelPackage) {
      return res.status(404).json({ error: 'Package not found' });
    }
    
    if (!travelPackage.available) {
      return res.status(400).json({ error: 'Package is not available for booking' });
    }
    
    if (guests > travelPackage.max_group_size) {
      return res.status(400).json({ 
        error: `Maximum group size for this package is ${travelPackage.max_group_size}` 
      });
    }
    
    // Create booking
    const booking = new Booking({
      user_id: req.user.user_id,
      package_id,
      package_name: travelPackage.name,
      destination_id: `package-${package_id}`, // Special identifier for package bookings
      check_in_date: new Date(check_in_date),
      check_out_date: new Date(check_out_date),
      guests,
      total_price: travelPackage.price * guests,
      booking_details,
      status: 'pending'
    });
    
    await booking.save();
    
    res.status(201).json(booking);
  } catch (error) {
    console.error('Book package error:', error);
    res.status(500).json({ error: 'Server error booking package' });
  }
});

module.exports = router;