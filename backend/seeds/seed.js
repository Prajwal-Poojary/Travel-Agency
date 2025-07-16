const mongoose = require('mongoose');
const User = require('../models/User');
const Destination = require('../models/Destination');
const Review = require('../models/Review');
const TravelPackage = require('../models/TravelPackage');
const Booking = require('../models/Booking');
require('dotenv').config();

// Sample destinations data
const destinations = [
  {
    name: "Maldives Paradise",
    country: "Maldives",
    city: "Malé",
    category: "Beach",
    description: "Experience the ultimate tropical paradise with crystal-clear waters, overwater bungalows, and world-class diving. The Maldives offers luxury resorts, pristine beaches, and vibrant marine life.",
    price_range: "$$$$",
    activities: ["Snorkeling", "Diving", "Spa", "Water Sports", "Sunset Cruise"],
    best_time_to_visit: "November to April",
    images: [
      "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
      "https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&q=80",
      "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80"
    ],
    coordinates: { latitude: 3.2028, longitude: 73.2207 },
    rating: 4.8,
    featured: true
  },
  {
    name: "Swiss Alps Adventure",
    country: "Switzerland",
    city: "Zermatt",
    category: "Mountain",
    description: "Breathtaking alpine scenery, world-class skiing, and charming mountain villages. Experience the majesty of the Matterhorn and enjoy hiking, skiing, and mountain railways.",
    price_range: "$$$",
    activities: ["Skiing", "Hiking", "Mountain Railway", "Cable Car", "Alpine Dining"],
    best_time_to_visit: "December to March, June to September",
    images: [
      "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
      "https://images.unsplash.com/photo-1485833077593-4278bba3f11f?w=800&q=80",
      "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80"
    ],
    coordinates: { latitude: 45.9763, longitude: 7.6586 },
    rating: 4.7,
    featured: true
  },
  {
    name: "Tokyo Metropolitan",
    country: "Japan",
    city: "Tokyo",
    category: "City",
    description: "A perfect blend of traditional culture and modern innovation. Experience ancient temples, cutting-edge technology, incredible cuisine, and vibrant neighborhoods.",
    price_range: "$$$",
    activities: ["Temple Visits", "Sushi Tours", "Shopping", "Nightlife", "Cultural Experiences"],
    best_time_to_visit: "March to May, October to November",
    images: [
      "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
      "https://images.unsplash.com/photo-1513407030348-c983a97b98d8?w=800&q=80",
      "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80"
    ],
    coordinates: { latitude: 35.6762, longitude: 139.6503 },
    rating: 4.6,
    featured: true
  },
  {
    name: "Santorini Sunset",
    country: "Greece",
    city: "Santorini",
    category: "Island",
    description: "Iconic blue-domed churches, stunning sunsets, and whitewashed buildings perched on dramatic cliffs. Perfect for romance and relaxation.",
    price_range: "$$$",
    activities: ["Sunset Viewing", "Wine Tasting", "Volcano Tours", "Beach Hopping", "Photography"],
    best_time_to_visit: "April to October",
    images: [
      "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80",
      "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=800&q=80",
      "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800&q=80"
    ],
    coordinates: { latitude: 36.3932, longitude: 25.4615 },
    rating: 4.5,
    featured: true
  },
  {
    name: "Dubai Luxury",
    country: "UAE",
    city: "Dubai",
    category: "City",
    description: "Ultra-modern city with luxury shopping, innovative architecture, and world-class entertainment. Experience the future of urban development.",
    price_range: "$$$$",
    activities: ["Shopping", "Skydiving", "Desert Safari", "Luxury Dining", "Architecture Tours"],
    best_time_to_visit: "November to March",
    images: [
      "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80",
      "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=800&q=80",
      "https://images.unsplash.com/photo-1544269150-0d0d9a9a7f45?w=800&q=80"
    ],
    coordinates: { latitude: 25.2048, longitude: 55.2708 },
    rating: 4.4,
    featured: true
  },
  {
    name: "Bali Spiritual",
    country: "Indonesia",
    city: "Ubud",
    category: "Cultural",
    description: "Spiritual retreat destination with lush rice terraces, ancient temples, and wellness experiences. Perfect for yoga, meditation, and cultural immersion.",
    price_range: "$$",
    activities: ["Yoga", "Temple Visits", "Rice Terrace Tours", "Spa Treatments", "Art Classes"],
    best_time_to_visit: "April to October",
    images: [
      "https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=800&q=80",
      "https://images.unsplash.com/photo-1555400082-0e8ba4a7618b?w=800&q=80",
      "https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?w=800&q=80"
    ],
    coordinates: { latitude: -8.5069, longitude: 115.2625 },
    rating: 4.3,
    featured: false
  },
  {
    name: "Iceland Aurora",
    country: "Iceland",
    city: "Reykjavik",
    category: "Adventure",
    description: "Land of fire and ice with dramatic landscapes, geysers, waterfalls, and the Northern Lights. Perfect for adventure seekers and nature lovers.",
    price_range: "$$$",
    activities: ["Northern Lights", "Glacier Hiking", "Hot Springs", "Whale Watching", "Photography"],
    best_time_to_visit: "September to March (Northern Lights), June to August (Hiking)",
    images: [
      "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
      "https://images.unsplash.com/photo-1483347756197-71ef80e95f73?w=800&q=80",
      "https://images.unsplash.com/photo-1531168556467-80aace4d20c5?w=800&q=80"
    ],
    coordinates: { latitude: 64.1466, longitude: -21.9426 },
    rating: 4.6,
    featured: false
  },
  {
    name: "Machu Picchu Trek",
    country: "Peru",
    city: "Cusco",
    category: "Historical",
    description: "Ancient Incan citadel high in the Andes Mountains. One of the New Seven Wonders of the World, offering incredible history and breathtaking views.",
    price_range: "$$",
    activities: ["Trekking", "Historical Tours", "Photography", "Local Culture", "Hiking"],
    best_time_to_visit: "May to September",
    images: [
      "https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&q=80",
      "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&q=80",
      "https://images.unsplash.com/photo-1539650116574-75c0c6d73f6e?w=800&q=80"
    ],
    coordinates: { latitude: -13.1631, longitude: -72.5450 },
    rating: 4.7,
    featured: false
  }
];

// Sample travel packages
const travelPackages = [
  {
    name: "Asian Adventure Circuit",
    description: "Explore the best of Asia with this comprehensive 14-day tour covering Tokyo's modern marvels and Bali's spiritual retreats.",
    destinations: ["Tokyo Metropolitan", "Bali Spiritual"],
    duration: "14 days",
    price: 3999,
    original_price: 4999,
    includes: [
      "Round-trip flights",
      "4-star accommodation",
      "Daily breakfast",
      "Guided tours",
      "Airport transfers",
      "Travel insurance"
    ],
    image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
    featured: true,
    max_group_size: 8,
    difficulty: "Moderate"
  },
  {
    name: "European Romance Package",
    description: "Perfect honeymoon package combining the alpine beauty of Switzerland with the romantic sunsets of Santorini.",
    destinations: ["Swiss Alps Adventure", "Santorini Sunset"],
    duration: "10 days",
    price: 4499,
    original_price: 5499,
    includes: [
      "Luxury accommodation",
      "Private transfers",
      "Romantic dinners",
      "Couple's spa treatments",
      "Champagne welcome",
      "Professional photography session"
    ],
    image: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80",
    featured: true,
    max_group_size: 2,
    difficulty: "Easy"
  },
  {
    name: "Luxury Tropical Escape",
    description: "Ultimate luxury experience combining the pristine beaches of Maldives with the modern luxury of Dubai.",
    destinations: ["Maldives Paradise", "Dubai Luxury"],
    duration: "12 days",
    price: 6999,
    original_price: 8999,
    includes: [
      "5-star resorts",
      "Private island access",
      "Overwater bungalow",
      "Helicopter transfers",
      "Michelin-starred dining",
      "Personal butler service"
    ],
    image: "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
    featured: true,
    max_group_size: 4,
    difficulty: "Easy"
  }
];

// Sample reviews
const reviews = [
  {
    username: "traveler_john",
    rating: 5,
    comment: "Absolutely incredible experience! The overwater bungalow was beyond my expectations. The staff was amazing and the snorkeling was world-class.",
    images: [],
    categories: { "Service": 5, "Accommodation": 5, "Activities": 5, "Value": 4 },
    verified_stay: true
  },
  {
    username: "adventure_sara",
    rating: 4,
    comment: "Great mountain adventure! The views were spectacular and the hiking trails were well-maintained. Weather was perfect during our visit.",
    images: [],
    categories: { "Activities": 5, "Scenery": 5, "Weather": 4, "Value": 4 },
    verified_stay: true
  }
];

// Seed function
async function seedDatabase() {
  try {
    console.log('🌱 Starting database seeding...');
    
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGO_URL || 'mongodb://localhost:27017/advanced_travel_db');
    console.log('✅ Connected to MongoDB');
    
    // Clear existing data
    await Promise.all([
      User.deleteMany({}),
      Destination.deleteMany({}),
      Review.deleteMany({}),
      TravelPackage.deleteMany({}),
      Booking.deleteMany({})
    ]);
    console.log('🗑️ Cleared existing data');
    
    // Seed destinations
    console.log('🏝️ Seeding destinations...');
    const createdDestinations = await Destination.insertMany(destinations);
    console.log(`✅ Created ${createdDestinations.length} destinations`);
    
    // Seed travel packages
    console.log('📦 Seeding travel packages...');
    const createdPackages = await TravelPackage.insertMany(travelPackages);
    console.log(`✅ Created ${createdPackages.length} travel packages`);
    
    // Create sample user
    console.log('👤 Creating sample user...');
    const sampleUser = new User({
      username: 'demo_user',
      email: 'demo@example.com',
      password: 'password123',
      full_name: 'Demo User'
    });
    await sampleUser.save();
    console.log('✅ Created sample user');
    
    // Seed reviews
    console.log('⭐ Seeding reviews...');
    const reviewsWithData = reviews.map((review, index) => ({
      ...review,
      user_id: sampleUser.user_id,
      destination_id: createdDestinations[index % createdDestinations.length].destination_id
    }));
    
    const createdReviews = await Review.insertMany(reviewsWithData);
    console.log(`✅ Created ${createdReviews.length} reviews`);
    
    // Create sample booking
    console.log('📅 Creating sample booking...');
    const sampleBooking = new Booking({
      user_id: sampleUser.user_id,
      destination_id: createdDestinations[0].destination_id,
      check_in_date: new Date('2024-08-01'),
      check_out_date: new Date('2024-08-07'),
      guests: 2,
      total_price: 2500,
      status: 'confirmed'
    });
    await sampleBooking.save();
    console.log('✅ Created sample booking');
    
    console.log('\n🎉 Database seeding completed successfully!');
    console.log('\n📊 Summary:');
    console.log(`   • ${createdDestinations.length} destinations`);
    console.log(`   • ${createdPackages.length} travel packages`);
    console.log(`   • ${createdReviews.length} reviews`);
    console.log(`   • 1 sample user (demo@example.com / password123)`);
    console.log(`   • 1 sample booking`);
    
  } catch (error) {
    console.error('❌ Seeding failed:', error);
  } finally {
    await mongoose.connection.close();
    console.log('🔒 Database connection closed');
  }
}

// Run seeding if called directly
if (require.main === module) {
  seedDatabase();
}

module.exports = seedDatabase;