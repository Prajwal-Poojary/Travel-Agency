const express = require('express');
const Destination = require('../models/Destination');
const Review = require('../models/Review');
const TravelPackage = require('../models/TravelPackage');
const Booking = require('../models/Booking');
const User = require('../models/User');

const router = express.Router();

// @route   GET /api/stats/popular-destinations
// @desc    Get most popular destinations
// @access  Public
router.get('/popular-destinations', async (req, res) => {
  try {
    const { limit = 10 } = req.query;
    
    const popularDestinations = await Destination.aggregate([
      {
        $lookup: {
          from: 'reviews',
          localField: 'destination_id',
          foreignField: 'destination_id',
          as: 'reviews'
        }
      },
      {
        $addFields: {
          review_count: { $size: '$reviews' },
          popularity_score: { $multiply: ['$rating', { $size: '$reviews' }] }
        }
      },
      {
        $sort: { popularity_score: -1 }
      },
      {
        $limit: parseInt(limit)
      },
      {
        $project: {
          destination_id: 1,
          name: 1,
          country: 1,
          city: 1,
          category: 1,
          rating: 1,
          review_count: 1,
          popularity_score: 1,
          images: { $slice: ['$images', 1] }
        }
      }
    ]);
    
    res.json(popularDestinations);
  } catch (error) {
    console.error('Get popular destinations error:', error);
    res.status(500).json({ error: 'Server error fetching popular destinations' });
  }
});

// @route   GET /api/stats/travel-insights
// @desc    Get general travel insights
// @access  Public
router.get('/travel-insights', async (req, res) => {
  try {
    const totalDestinations = await Destination.countDocuments({});
    const totalReviews = await Review.countDocuments({});
    const totalPackages = await TravelPackage.countDocuments({});
    const totalBookings = await Booking.countDocuments({});
    const totalUsers = await User.countDocuments({});
    
    // Get average rating across all destinations
    const avgRatingResult = await Destination.aggregate([
      { $group: { _id: null, avg_rating: { $avg: '$rating' } } }
    ]);
    const avgRating = avgRatingResult.length > 0 ? avgRatingResult[0].avg_rating : 0;
    
    // Get most popular category
    const popularCategoryResult = await Destination.aggregate([
      { $group: { _id: '$category', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 1 }
    ]);
    const popularCategory = popularCategoryResult.length > 0 ? popularCategoryResult[0]._id : 'Unknown';
    
    // Get booking statistics
    const bookingStats = await Booking.aggregate([
      { $group: { _id: '$status', count: { $sum: 1 } } }
    ]);
    
    // Get monthly booking trends (last 6 months)
    const monthlyBookings = await Booking.aggregate([
      {
        $match: {
          created_at: {
            $gte: new Date(new Date().setMonth(new Date().getMonth() - 6))
          }
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$created_at' },
            month: { $month: '$created_at' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } }
    ]);
    
    res.json({
      total_destinations: totalDestinations,
      total_reviews: totalReviews,
      total_packages: totalPackages,
      total_bookings: totalBookings,
      total_users: totalUsers,
      average_rating: Math.round(avgRating * 10) / 10,
      most_popular_category: popularCategory,
      booking_stats: bookingStats,
      monthly_booking_trends: monthlyBookings
    });
  } catch (error) {
    console.error('Get travel insights error:', error);
    res.status(500).json({ error: 'Server error fetching travel insights' });
  }
});

// @route   GET /api/stats/destinations-by-country
// @desc    Get destinations grouped by country
// @access  Public
router.get('/destinations-by-country', async (req, res) => {
  try {
    const destinationsByCountry = await Destination.aggregate([
      {
        $group: {
          _id: '$country',
          count: { $sum: 1 },
          destinations: {
            $push: {
              destination_id: '$destination_id',
              name: '$name',
              city: '$city',
              rating: '$rating',
              category: '$category'
            }
          }
        }
      },
      { $sort: { count: -1 } }
    ]);
    
    res.json(destinationsByCountry);
  } catch (error) {
    console.error('Get destinations by country error:', error);
    res.status(500).json({ error: 'Server error fetching destinations by country' });
  }
});

// @route   GET /api/stats/revenue-stats
// @desc    Get revenue statistics
// @access  Public
router.get('/revenue-stats', async (req, res) => {
  try {
    const revenueStats = await Booking.aggregate([
      {
        $match: {
          status: { $in: ['confirmed', 'completed'] }
        }
      },
      {
        $group: {
          _id: null,
          total_revenue: { $sum: '$total_price' },
          average_booking_value: { $avg: '$total_price' },
          total_bookings: { $sum: 1 }
        }
      }
    ]);
    
    // Monthly revenue trends
    const monthlyRevenue = await Booking.aggregate([
      {
        $match: {
          status: { $in: ['confirmed', 'completed'] },
          created_at: {
            $gte: new Date(new Date().setMonth(new Date().getMonth() - 12))
          }
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$created_at' },
            month: { $month: '$created_at' }
          },
          revenue: { $sum: '$total_price' },
          bookings: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } }
    ]);
    
    const stats = revenueStats.length > 0 ? revenueStats[0] : {
      total_revenue: 0,
      average_booking_value: 0,
      total_bookings: 0
    };
    
    res.json({
      ...stats,
      monthly_revenue_trends: monthlyRevenue
    });
  } catch (error) {
    console.error('Get revenue stats error:', error);
    res.status(500).json({ error: 'Server error fetching revenue statistics' });
  }
});

// @route   GET /api/stats/search-suggestions
// @desc    Get search suggestions
// @access  Public
router.get('/search-suggestions', async (req, res) => {
  try {
    const { q } = req.query;
    
    if (!q || q.length < 2) {
      return res.json([]);
    }
    
    const suggestions = await Destination.find(
      {
        $or: [
          { name: { $regex: q, $options: 'i' } },
          { city: { $regex: q, $options: 'i' } },
          { country: { $regex: q, $options: 'i' } },
          { category: { $regex: q, $options: 'i' } }
        ]
      },
      {
        destination_id: 1,
        name: 1,
        city: 1,
        country: 1,
        category: 1
      }
    ).limit(8);
    
    const formattedSuggestions = suggestions.map(suggestion => ({
      destination_id: suggestion.destination_id,
      name: suggestion.name,
      location: `${suggestion.city}, ${suggestion.country}`,
      category: suggestion.category
    }));
    
    res.json(formattedSuggestions);
  } catch (error) {
    console.error('Get search suggestions error:', error);
    res.status(500).json({ error: 'Server error fetching search suggestions' });
  }
});

module.exports = router;