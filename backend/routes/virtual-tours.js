const express = require('express');
const { body, validationResult, query } = require('express-validator');
const VirtualTour = require('../models/VirtualTour');
const auth = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/virtual-tours
// @desc    Get all virtual tours with filters
// @access  Public
router.get('/', [
  query('search').optional().isString(),
  query('country').optional().isString(),
  query('tour_type').optional().isIn(['360_video', 'interactive_360', 'drone_360', 'cultural_360']),
  query('featured_only').optional().isBoolean(),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('skip').optional().isInt({ min: 0 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { search, country, tour_type, featured_only, limit = 50, skip = 0 } = req.query;
    
    let query = { active: true };
    
    // Search filter
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { city: { $regex: search, $options: 'i' } },
        { country: { $regex: search, $options: 'i' } },
        { tags: { $in: [new RegExp(search, 'i')] } }
      ];
    }
    
    // Country filter
    if (country) {
      query.country = { $regex: country, $options: 'i' };
    }
    
    // Tour type filter
    if (tour_type) {
      query.tour_type = tour_type;
    }
    
    // Featured only filter
    if (featured_only === 'true') {
      query.featured = true;
    }
    
    const tours = await VirtualTour.find(query)
      .sort({ featured: -1, views: -1, created_at: -1 })
      .limit(parseInt(limit))
      .skip(parseInt(skip));
    
    res.json(tours);
  } catch (error) {
    console.error('Get virtual tours error:', error);
    res.status(500).json({ error: 'Server error fetching virtual tours' });
  }
});

// @route   GET /api/virtual-tours/featured
// @desc    Get featured virtual tours
// @access  Public
router.get('/featured', [
  query('limit').optional().isInt({ min: 1, max: 20 })
], async (req, res) => {
  try {
    const { limit = 6 } = req.query;
    
    const tours = await VirtualTour.find({ 
      featured: true, 
      active: true 
    })
    .sort({ views: -1, created_at: -1 })
    .limit(parseInt(limit));
    
    res.json(tours);
  } catch (error) {
    console.error('Get featured virtual tours error:', error);
    res.status(500).json({ error: 'Server error fetching featured virtual tours' });
  }
});

// @route   GET /api/virtual-tours/types
// @desc    Get virtual tour types with counts
// @access  Public
router.get('/types', async (req, res) => {
  try {
    const types = await VirtualTour.aggregate([
      { $match: { active: true } },
      { $group: { _id: '$tour_type', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);
    
    const formattedTypes = types.map(type => ({
      type: type._id,
      count: type.count,
      label: type._id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }));
    
    res.json(formattedTypes);
  } catch (error) {
    console.error('Get virtual tour types error:', error);
    res.status(500).json({ error: 'Server error fetching tour types' });
  }
});

// @route   GET /api/virtual-tours/countries
// @desc    Get all available countries for virtual tours
// @access  Public
router.get('/countries', async (req, res) => {
  try {
    const countries = await VirtualTour.distinct('country', { active: true });
    res.json(countries);
  } catch (error) {
    console.error('Get virtual tour countries error:', error);
    res.status(500).json({ error: 'Server error fetching countries' });
  }
});

// @route   GET /api/virtual-tours/:tour_id
// @desc    Get single virtual tour
// @access  Public
router.get('/:tour_id', async (req, res) => {
  try {
    const { tour_id } = req.params;
    
    const tour = await VirtualTour.findOne({ 
      tour_id, 
      active: true 
    });
    
    if (!tour) {
      return res.status(404).json({ error: 'Virtual tour not found' });
    }
    
    // Increment view count
    tour.views += 1;
    await tour.save();
    
    res.json(tour);
  } catch (error) {
    console.error('Get virtual tour error:', error);
    res.status(500).json({ error: 'Server error fetching virtual tour' });
  }
});

// @route   GET /api/virtual-tours/:tour_id/analytics
// @desc    Get virtual tour analytics
// @access  Public
router.get('/:tour_id/analytics', async (req, res) => {
  try {
    const { tour_id } = req.params;
    
    const tour = await VirtualTour.findOne({ 
      tour_id, 
      active: true 
    });
    
    if (!tour) {
      return res.status(404).json({ error: 'Virtual tour not found' });
    }
    
    const analytics = {
      tour_id: tour.tour_id,
      name: tour.name,
      views: tour.views,
      rating: tour.rating,
      duration: tour.duration,
      type: tour.tour_type,
      featured: tour.featured,
      highlights_count: tour.highlights.length,
      interactive_elements_count: tour.interactive_elements.length,
      created_at: tour.created_at
    };
    
    res.json(analytics);
  } catch (error) {
    console.error('Get virtual tour analytics error:', error);
    res.status(500).json({ error: 'Server error fetching analytics' });
  }
});

// @route   POST /api/virtual-tours
// @desc    Create new virtual tour
// @access  Private (Admin)
router.post('/', auth, [
  body('name').isLength({ min: 1, max: 200 }).trim(),
  body('description').isLength({ min: 1, max: 1000 }),
  body('country').isLength({ min: 1, max: 100 }).trim(),
  body('city').isLength({ min: 1, max: 100 }).trim(),
  body('tour_type').isIn(['360_video', 'interactive_360', 'drone_360', 'cultural_360']),
  body('video_url').isURL(),
  body('thumbnail').isURL(),
  body('duration').isLength({ min: 1, max: 10 }),
  body('coordinates.latitude').isFloat({ min: -90, max: 90 }),
  body('coordinates.longitude').isFloat({ min: -180, max: 180 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const tour = new VirtualTour(req.body);
    await tour.save();
    
    res.status(201).json(tour);
  } catch (error) {
    console.error('Create virtual tour error:', error);
    res.status(500).json({ error: 'Server error creating virtual tour' });
  }
});

// @route   PUT /api/virtual-tours/:tour_id
// @desc    Update virtual tour
// @access  Private (Admin)
router.put('/:tour_id', auth, [
  body('name').optional().isLength({ min: 1, max: 200 }).trim(),
  body('description').optional().isLength({ min: 1, max: 1000 }),
  body('country').optional().isLength({ min: 1, max: 100 }).trim(),
  body('city').optional().isLength({ min: 1, max: 100 }).trim(),
  body('tour_type').optional().isIn(['360_video', 'interactive_360', 'drone_360', 'cultural_360']),
  body('video_url').optional().isURL(),
  body('thumbnail').optional().isURL(),
  body('duration').optional().isLength({ min: 1, max: 10 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { tour_id } = req.params;
    
    const tour = await VirtualTour.findOneAndUpdate(
      { tour_id },
      { ...req.body, updated_at: Date.now() },
      { new: true }
    );
    
    if (!tour) {
      return res.status(404).json({ error: 'Virtual tour not found' });
    }
    
    res.json(tour);
  } catch (error) {
    console.error('Update virtual tour error:', error);
    res.status(500).json({ error: 'Server error updating virtual tour' });
  }
});

// @route   DELETE /api/virtual-tours/:tour_id
// @desc    Delete virtual tour (soft delete)
// @access  Private (Admin)
router.delete('/:tour_id', auth, async (req, res) => {
  try {
    const { tour_id } = req.params;
    
    const tour = await VirtualTour.findOneAndUpdate(
      { tour_id },
      { active: false, updated_at: Date.now() },
      { new: true }
    );
    
    if (!tour) {
      return res.status(404).json({ error: 'Virtual tour not found' });
    }
    
    res.json({ message: 'Virtual tour deleted successfully' });
  } catch (error) {
    console.error('Delete virtual tour error:', error);
    res.status(500).json({ error: 'Server error deleting virtual tour' });
  }
});

module.exports = router;