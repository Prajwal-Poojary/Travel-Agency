const express = require('express');
const { body, validationResult } = require('express-validator');
const Review = require('../models/Review');
const Destination = require('../models/Destination');
const auth = require('../middleware/auth');

const router = express.Router();

// @route   POST /api/reviews
// @desc    Create new review
// @access  Private
router.post('/', auth, [
  body('destination_id').notEmpty(),
  body('rating').isInt({ min: 1, max: 5 }),
  body('comment').isLength({ min: 1, max: 1000 }),
  body('images').optional().isArray(),
  body('categories').optional().isObject(),
  body('verified_stay').optional().isBoolean()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { destination_id, rating, comment, images, categories, verified_stay } = req.body;

    // Check if destination exists
    const destination = await Destination.findOne({ destination_id });
    if (!destination) {
      return res.status(404).json({ error: 'Destination not found' });
    }

    // Check if user already reviewed this destination
    const existingReview = await Review.findOne({
      user_id: req.user.user_id,
      destination_id
    });

    if (existingReview) {
      return res.status(400).json({ error: 'You have already reviewed this destination' });
    }

    const review = new Review({
      user_id: req.user.user_id,
      username: req.user.username,
      destination_id,
      rating,
      comment,
      images: images || [],
      categories: categories || {},
      verified_stay: verified_stay || false
    });

    await review.save();

    // Update destination rating
    const reviews = await Review.find({ destination_id });
    const avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length;
    
    await Destination.findOneAndUpdate(
      { destination_id },
      { rating: Math.round(avgRating * 10) / 10 }
    );
    
    res.status(201).json(review);
  } catch (error) {
    console.error('Create review error:', error);
    res.status(500).json({ error: 'Server error creating review' });
  }
});

// @route   GET /api/reviews/:destination_id
// @desc    Get reviews for destination
// @access  Public
router.get('/:destination_id', async (req, res) => {
  try {
    const { destination_id } = req.params;
    const { limit = 50 } = req.query;

    const reviews = await Review.find({ destination_id })
      .sort({ created_at: -1 })
      .limit(parseInt(limit));
    
    res.json(reviews);
  } catch (error) {
    console.error('Get reviews error:', error);
    res.status(500).json({ error: 'Server error fetching reviews' });
  }
});

// @route   POST /api/reviews/:review_id/helpful
// @desc    Mark review as helpful
// @access  Private
router.post('/:review_id/helpful', auth, async (req, res) => {
  try {
    const { review_id } = req.params;

    const review = await Review.findOne({ review_id });
    
    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    review.helpful_count += 1;
    await review.save();
    
    res.json({ message: 'Review marked as helpful' });
  } catch (error) {
    console.error('Mark review helpful error:', error);
    res.status(500).json({ error: 'Server error marking review as helpful' });
  }
});

// @route   GET /api/reviews/:destination_id/stats
// @desc    Get review statistics for destination
// @access  Public
router.get('/:destination_id/stats', async (req, res) => {
  try {
    const { destination_id } = req.params;

    const totalReviews = await Review.countDocuments({ destination_id });
    
    const ratingStats = await Review.aggregate([
      { $match: { destination_id } },
      { $group: { _id: '$rating', count: { $sum: 1 } } }
    ]);

    const avgRatingResult = await Review.aggregate([
      { $match: { destination_id } },
      { $group: { _id: null, avg_rating: { $avg: '$rating' } } }
    ]);

    const avgRating = avgRatingResult.length > 0 ? avgRatingResult[0].avg_rating : 0;

    res.json({
      total_reviews: totalReviews,
      average_rating: Math.round(avgRating * 10) / 10,
      rating_distribution: ratingStats
    });
  } catch (error) {
    console.error('Get review stats error:', error);
    res.status(500).json({ error: 'Server error fetching review statistics' });
  }
});

// @route   PUT /api/reviews/:review_id
// @desc    Update review
// @access  Private
router.put('/:review_id', auth, [
  body('rating').optional().isInt({ min: 1, max: 5 }),
  body('comment').optional().isLength({ min: 1, max: 1000 }),
  body('images').optional().isArray(),
  body('categories').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { review_id } = req.params;
    const updates = req.body;

    const review = await Review.findOne({ 
      review_id,
      user_id: req.user.user_id 
    });
    
    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    // Update review fields
    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        review[key] = updates[key];
      }
    });

    await review.save();

    // Update destination rating if rating changed
    if (updates.rating) {
      const reviews = await Review.find({ destination_id: review.destination_id });
      const avgRating = reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length;
      
      await Destination.findOneAndUpdate(
        { destination_id: review.destination_id },
        { rating: Math.round(avgRating * 10) / 10 }
      );
    }
    
    res.json(review);
  } catch (error) {
    console.error('Update review error:', error);
    res.status(500).json({ error: 'Server error updating review' });
  }
});

// @route   DELETE /api/reviews/:review_id
// @desc    Delete review
// @access  Private
router.delete('/:review_id', auth, async (req, res) => {
  try {
    const { review_id } = req.params;
    
    const review = await Review.findOne({ 
      review_id,
      user_id: req.user.user_id 
    });
    
    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    const destination_id = review.destination_id;
    await Review.findOneAndDelete({ review_id });

    // Update destination rating
    const reviews = await Review.find({ destination_id });
    const avgRating = reviews.length > 0 
      ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length 
      : 0;
    
    await Destination.findOneAndUpdate(
      { destination_id },
      { rating: Math.round(avgRating * 10) / 10 }
    );
    
    res.json({ message: 'Review deleted successfully' });
  } catch (error) {
    console.error('Delete review error:', error);
    res.status(500).json({ error: 'Server error deleting review' });
  }
});

module.exports = router;