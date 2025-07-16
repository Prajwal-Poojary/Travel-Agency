const express = require('express');
const { body, validationResult } = require('express-validator');
const Booking = require('../models/Booking');
const Destination = require('../models/Destination');
const auth = require('../middleware/auth');

const router = express.Router();

// @route   POST /api/bookings
// @desc    Create new booking
// @access  Private
router.post('/', auth, [
  body('destination_id').notEmpty(),
  body('check_in_date').isISO8601(),
  body('check_out_date').isISO8601(),
  body('guests').isInt({ min: 1, max: 20 }),
  body('special_requests').optional().isLength({ max: 500 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { destination_id, check_in_date, check_out_date, guests, special_requests } = req.body;

    // Check if destination exists
    const destination = await Destination.findOne({ destination_id });
    if (!destination) {
      return res.status(404).json({ error: 'Destination not found' });
    }

    // Validate dates
    const checkIn = new Date(check_in_date);
    const checkOut = new Date(check_out_date);
    const today = new Date();
    
    if (checkIn < today) {
      return res.status(400).json({ error: 'Check-in date cannot be in the past' });
    }
    
    if (checkIn >= checkOut) {
      return res.status(400).json({ error: 'Check-out date must be after check-in date' });
    }

    // Calculate total price (simplified logic)
    const days = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
    const basePrice = { '$': 100, '$$': 200, '$$$': 400, '$$$$': 800 }[destination.price_range] || 200;
    const total_price = basePrice * days * guests;

    const booking = new Booking({
      user_id: req.user.user_id,
      destination_id,
      check_in_date: checkIn,
      check_out_date: checkOut,
      guests,
      total_price,
      special_requests
    });

    await booking.save();
    
    res.status(201).json(booking);
  } catch (error) {
    console.error('Create booking error:', error);
    res.status(500).json({ error: 'Server error creating booking' });
  }
});

// @route   GET /api/bookings
// @desc    Get user bookings
// @access  Private
router.get('/', auth, async (req, res) => {
  try {
    const bookings = await Booking.find({ user_id: req.user.user_id })
      .sort({ created_at: -1 });
    
    // Add destination details to each booking
    const bookingsWithDestinations = await Promise.all(
      bookings.map(async (booking) => {
        const destination = await Destination.findOne({ 
          destination_id: booking.destination_id 
        });
        
        return {
          ...booking.toObject(),
          destination: destination ? {
            name: destination.name,
            city: destination.city,
            country: destination.country,
            images: destination.images.slice(0, 1)
          } : null
        };
      })
    );
    
    res.json(bookingsWithDestinations);
  } catch (error) {
    console.error('Get bookings error:', error);
    res.status(500).json({ error: 'Server error fetching bookings' });
  }
});

// @route   GET /api/bookings/:booking_id
// @desc    Get single booking
// @access  Private
router.get('/:booking_id', auth, async (req, res) => {
  try {
    const { booking_id } = req.params;
    
    const booking = await Booking.findOne({ 
      booking_id,
      user_id: req.user.user_id 
    });
    
    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }
    
    // Add destination details
    const destination = await Destination.findOne({ 
      destination_id: booking.destination_id 
    });
    
    res.json({
      ...booking.toObject(),
      destination: destination ? {
        name: destination.name,
        city: destination.city,
        country: destination.country,
        images: destination.images,
        description: destination.description
      } : null
    });
  } catch (error) {
    console.error('Get booking error:', error);
    res.status(500).json({ error: 'Server error fetching booking' });
  }
});

// @route   PUT /api/bookings/:booking_id
// @desc    Update booking
// @access  Private
router.put('/:booking_id', auth, [
  body('check_in_date').optional().isISO8601(),
  body('check_out_date').optional().isISO8601(),
  body('guests').optional().isInt({ min: 1, max: 20 }),
  body('special_requests').optional().isLength({ max: 500 }),
  body('status').optional().isIn(['pending', 'confirmed', 'cancelled', 'completed'])
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { booking_id } = req.params;
    const updates = req.body;

    const booking = await Booking.findOne({ 
      booking_id,
      user_id: req.user.user_id 
    });
    
    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Update booking fields
    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        booking[key] = updates[key];
      }
    });

    await booking.save();
    
    res.json(booking);
  } catch (error) {
    console.error('Update booking error:', error);
    res.status(500).json({ error: 'Server error updating booking' });
  }
});

// @route   DELETE /api/bookings/:booking_id
// @desc    Cancel booking
// @access  Private
router.delete('/:booking_id', auth, async (req, res) => {
  try {
    const { booking_id } = req.params;
    
    const booking = await Booking.findOne({ 
      booking_id,
      user_id: req.user.user_id 
    });
    
    if (!booking) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    booking.status = 'cancelled';
    await booking.save();
    
    res.json({ message: 'Booking cancelled successfully' });
  } catch (error) {
    console.error('Cancel booking error:', error);
    res.status(500).json({ error: 'Server error cancelling booking' });
  }
});

module.exports = router;