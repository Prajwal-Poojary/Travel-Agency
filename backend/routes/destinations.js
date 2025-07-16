const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Destination = require('../models/Destination');
const Review = require('../models/Review');
const auth = require('../middleware/auth');
const axios = require('axios');

const router = express.Router();

// Weather service function
const getWeatherData = async (city) => {
  if (!process.env.WEATHER_API_KEY || process.env.WEATHER_API_KEY === 'your-openweathermap-api-key-here') {
    return { 
      error: 'Weather API key not configured',
      temperature: 'N/A',
      description: 'Weather data unavailable'
    };
  }
  
  try {
    const url = `http://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${process.env.WEATHER_API_KEY}&units=metric`;
    const response = await axios.get(url);
    
    if (response.status === 200) {
      return {
        temperature: response.data.main.temp,
        description: response.data.weather[0].description,
        humidity: response.data.main.humidity,
        wind_speed: response.data.wind.speed
      };
    } else {
      return { error: 'Weather data not available' };
    }
  } catch (error) {
    return { 
      error: 'Weather service unavailable',
      temperature: 'N/A',
      description: 'Weather data unavailable'
    };
  }
};

// @route   GET /api/destinations
// @desc    Get all destinations with filters
// @access  Public
router.get('/', [
  query('search').optional().isString(),
  query('country').optional().isString(),
  query('category').optional().isString(),
  query('activity').optional().isString(),
  query('featured_only').optional().isBoolean(),
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { search, country, category, activity, featured_only, limit = 100 } = req.query;
    
    let query = {};
    
    // Search filter
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { city: { $regex: search, $options: 'i' } },
        { country: { $regex: search, $options: 'i' } }
      ];
    }
    
    // Country filter
    if (country) {
      query.country = { $regex: country, $options: 'i' };
    }
    
    // Category filter
    if (category) {
      query.category = { $regex: category, $options: 'i' };
    }
    
    // Activity filter
    if (activity) {
      query.activities = { $in: [activity] };
    }
    
    // Featured only filter
    if (featured_only === 'true') {
      query.featured = true;
    }
    
    const destinations = await Destination.find(query).limit(parseInt(limit));
    
    // Add weather data for each destination
    const destinationsWithWeather = await Promise.all(
      destinations.map(async (destination) => {
        const weatherData = await getWeatherData(destination.city);
        return {
          ...destination.toObject(),
          weather: weatherData
        };
      })
    );
    
    res.json(destinationsWithWeather);
  } catch (error) {
    console.error('Get destinations error:', error);
    res.status(500).json({ error: 'Server error fetching destinations' });
  }
});

// @route   GET /api/destinations/countries
// @desc    Get all available countries
// @access  Public
router.get('/countries', async (req, res) => {
  try {
    const countries = await Destination.distinct('country');
    res.json(countries);
  } catch (error) {
    console.error('Get countries error:', error);
    res.status(500).json({ error: 'Server error fetching countries' });
  }
});

// @route   GET /api/destinations/activities
// @desc    Get all available activities
// @access  Public
router.get('/activities', async (req, res) => {
  try {
    const activities = await Destination.distinct('activities');
    res.json(activities);
  } catch (error) {
    console.error('Get activities error:', error);
    res.status(500).json({ error: 'Server error fetching activities' });
  }
});

// @route   GET /api/destinations/featured
// @desc    Get featured destinations
// @access  Public
router.get('/featured', async (req, res) => {
  try {
    const destinations = await Destination.find({ featured: true }).limit(6);
    
    // Add weather data for each destination
    const destinationsWithWeather = await Promise.all(
      destinations.map(async (destination) => {
        const weatherData = await getWeatherData(destination.city);
        return {
          ...destination.toObject(),
          weather: weatherData
        };
      })
    );
    
    res.json(destinationsWithWeather);
  } catch (error) {
    console.error('Get featured destinations error:', error);
    res.status(500).json({ error: 'Server error fetching featured destinations' });
  }
});

// @route   GET /api/destinations/categories
// @desc    Get destination categories with counts
// @access  Public
router.get('/categories', async (req, res) => {
  try {
    const categories = await Destination.aggregate([
      { $group: { _id: '$category', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);
    
    const formattedCategories = categories.map(cat => ({
      name: cat._id,
      count: cat.count
    }));
    
    res.json(formattedCategories);
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({ error: 'Server error fetching categories' });
  }
});

// @route   GET /api/destinations/by-category/:category
// @desc    Get destinations by category
// @access  Public
router.get('/by-category/:category', [
  query('limit').optional().isInt({ min: 1, max: 100 })
], async (req, res) => {
  try {
    const { category } = req.params;
    const { limit = 20 } = req.query;
    
    const destinations = await Destination.find({
      category: { $regex: category, $options: 'i' }
    }).limit(parseInt(limit));
    
    // Add weather data for each destination
    const destinationsWithWeather = await Promise.all(
      destinations.map(async (destination) => {
        const weatherData = await getWeatherData(destination.city);
        return {
          ...destination.toObject(),
          weather: weatherData
        };
      })
    );
    
    res.json(destinationsWithWeather);
  } catch (error) {
    console.error('Get destinations by category error:', error);
    res.status(500).json({ error: 'Server error fetching destinations by category' });
  }
});

// @route   GET /api/destinations/:destination_id
// @desc    Get single destination
// @access  Public
router.get('/:destination_id', async (req, res) => {
  try {
    const { destination_id } = req.params;
    
    const destination = await Destination.findOne({ destination_id });
    
    if (!destination) {
      return res.status(404).json({ error: 'Destination not found' });
    }
    
    // Add weather data
    const weatherData = await getWeatherData(destination.city);
    
    res.json({
      ...destination.toObject(),
      weather: weatherData
    });
  } catch (error) {
    console.error('Get destination error:', error);
    res.status(500).json({ error: 'Server error fetching destination' });
  }
});

// @route   POST /api/destinations
// @desc    Create new destination
// @access  Private (Admin)
router.post('/', auth, [
  body('name').isLength({ min: 1, max: 200 }).trim(),
  body('country').isLength({ min: 1, max: 100 }).trim(),
  body('city').isLength({ min: 1, max: 100 }).trim(),
  body('category').isLength({ min: 1, max: 50 }).trim(),
  body('description').isLength({ min: 1, max: 2000 }),
  body('price_range').isIn(['$', '$$', '$$$', '$$$$']),
  body('activities').isArray(),
  body('best_time_to_visit').isLength({ min: 1, max: 200 }),
  body('images').isArray().notEmpty(),
  body('coordinates.latitude').isFloat({ min: -90, max: 90 }),
  body('coordinates.longitude').isFloat({ min: -180, max: 180 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const destination = new Destination(req.body);
    await destination.save();
    
    res.status(201).json(destination);
  } catch (error) {
    console.error('Create destination error:', error);
    res.status(500).json({ error: 'Server error creating destination' });
  }
});

module.exports = router;