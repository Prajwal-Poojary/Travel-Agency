const mongoose = require('mongoose');
const VirtualTour = require('../models/VirtualTour');
require('dotenv').config();

const virtualToursData = [
  {
    name: "Maldives Paradise",
    description: "Experience the crystal-clear waters and overwater bungalows of the Maldives through our immersive 360° virtual tour. Discover pristine beaches, vibrant coral reefs, and luxury resort experiences.",
    country: "Maldives",
    city: "Male",
    tour_type: "360_video",
    video_url: "https://www.youtube.com/embed/8Md2nRkQ9Qw",
    thumbnail: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=450&fit=crop",
    duration: "12:30",
    featured: true,
    views: 15420,
    rating: 4.8,
    features: ["360° Views", "Audio Guide", "HD Quality", "Underwater Scenes"],
    highlights: [
      {
        time: "2:15",
        title: "Overwater Bungalows",
        description: "Tour the luxurious overwater villas with glass floors"
      },
      {
        time: "5:45",
        title: "Coral Reef Diving",
        description: "Experience the vibrant underwater coral gardens"
      },
      {
        time: "8:20",
        title: "Sunset Views",
        description: "Watch the breathtaking Maldivian sunset"
      },
      {
        time: "10:30",
        title: "Local Culture",
        description: "Visit a traditional Maldivian fishing village"
      }
    ],
    interactive_elements: [
      {
        time: "3:00",
        type: "hotspot",
        info: "Click to learn about marine life conservation"
      },
      {
        time: "6:30",
        type: "info_panel",
        info: "Discover the best diving spots in the Maldives"
      }
    ],
    coordinates: {
      latitude: 3.2028,
      longitude: 73.2207
    },
    tags: ["tropical", "luxury", "diving", "beach", "romance"],
    language: "English"
  },
  {
    name: "Swiss Alps Adventure",
    description: "Journey through the majestic Swiss Alps with breathtaking mountain views, pristine lakes, and charming alpine villages. Experience world-class skiing and mountain adventures.",
    country: "Switzerland",
    city: "Interlaken",
    tour_type: "drone_360",
    video_url: "https://www.youtube.com/embed/8c5rrxZC-I8",
    thumbnail: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=450&fit=crop",
    duration: "15:45",
    featured: true,
    views: 12840,
    rating: 4.9,
    features: ["Drone Views", "4K Quality", "Mountain Peaks", "Alpine Lakes"],
    highlights: [
      {
        time: "1:30",
        title: "Jungfraujoch",
        description: "Visit the 'Top of Europe' with spectacular glacial views"
      },
      {
        time: "4:20",
        title: "Lake Brienz",
        description: "Fly over the turquoise alpine lake"
      },
      {
        time: "7:15",
        title: "Matterhorn",
        description: "Aerial view of the iconic pyramid-shaped peak"
      },
      {
        time: "11:30",
        title: "Alpine Villages",
        description: "Explore charming Swiss mountain villages"
      }
    ],
    interactive_elements: [
      {
        time: "2:45",
        type: "navigation",
        info: "Choose your preferred mountain trail"
      },
      {
        time: "8:00",
        type: "info_panel",
        info: "Learn about Swiss alpine ecology"
      }
    ],
    coordinates: {
      latitude: 46.6863,
      longitude: 7.8632
    },
    tags: ["mountains", "skiing", "adventure", "nature", "hiking"],
    language: "English"
  },
  {
    name: "Tokyo Metropolitan",
    description: "Immerse yourself in the vibrant culture of Tokyo, from ancient temples to modern skyscrapers. Experience the perfect blend of traditional Japan and cutting-edge technology.",
    country: "Japan",
    city: "Tokyo",
    tour_type: "cultural_360",
    video_url: "https://www.youtube.com/embed/VQGm2b0wGOQ",
    thumbnail: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=450&fit=crop",
    duration: "18:20",
    featured: true,
    views: 18960,
    rating: 4.7,
    features: ["Cultural Sites", "Street Views", "Temple Tours", "Modern Architecture"],
    highlights: [
      {
        time: "2:00",
        title: "Senso-ji Temple",
        description: "Explore Tokyo's oldest Buddhist temple"
      },
      {
        time: "5:30",
        title: "Shibuya Crossing",
        description: "Experience the world's busiest pedestrian crossing"
      },
      {
        time: "9:45",
        title: "Tokyo Skytree",
        description: "Panoramic views from Japan's tallest structure"
      },
      {
        time: "13:15",
        title: "Tsukiji Fish Market",
        description: "Witness the famous tuna auction and fresh sushi"
      }
    ],
    interactive_elements: [
      {
        time: "4:00",
        type: "quiz",
        info: "Test your knowledge of Japanese culture"
      },
      {
        time: "10:30",
        type: "info_panel",
        info: "Learn about Tokyo's history and development"
      }
    ],
    coordinates: {
      latitude: 35.6762,
      longitude: 139.6503
    },
    tags: ["culture", "temples", "modern", "food", "technology"],
    language: "English"
  },
  {
    name: "Santorini Sunset",
    description: "Experience the magical sunsets and white-washed buildings of Santorini. Walk through picturesque villages, explore ancient ruins, and enjoy the stunning Aegean Sea views.",
    country: "Greece",
    city: "Santorini",
    tour_type: "interactive_360",
    video_url: "https://www.youtube.com/embed/1_KQgAOlVZU",
    thumbnail: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&h=450&fit=crop",
    duration: "14:15",
    featured: true,
    views: 14720,
    rating: 4.6,
    features: ["Interactive Hotspots", "Sunset Views", "Village Tours", "Archaeological Sites"],
    highlights: [
      {
        time: "1:45",
        title: "Oia Village",
        description: "Stroll through the famous blue-domed churches"
      },
      {
        time: "4:30",
        title: "Akrotiri Ruins",
        description: "Discover the ancient Minoan civilization"
      },
      {
        time: "8:00",
        title: "Caldera Views",
        description: "Marvel at the volcanic caldera formation"
      },
      {
        time: "11:20",
        title: "Wine Tasting",
        description: "Experience local Assyrtiko wine varieties"
      }
    ],
    interactive_elements: [
      {
        time: "3:15",
        type: "hotspot",
        info: "Click to explore inside a traditional cave house"
      },
      {
        time: "6:45",
        type: "navigation",
        info: "Choose between sunset or sunrise viewing spots"
      }
    ],
    coordinates: {
      latitude: 36.3932,
      longitude: 25.4615
    },
    tags: ["sunset", "islands", "architecture", "wine", "romantic"],
    language: "English"
  },
  {
    name: "Dubai Skyline",
    description: "Soar above the futuristic skyline of Dubai and experience the city's architectural marvels, luxury shopping, and desert adventures through stunning aerial footage.",
    country: "UAE",
    city: "Dubai",
    tour_type: "drone_360",
    video_url: "https://www.youtube.com/embed/au2qp8SqEus",
    thumbnail: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&h=450&fit=crop",
    duration: "16:30",
    featured: false,
    views: 9840,
    rating: 4.5,
    features: ["Drone Footage", "Skyscrapers", "Desert Views", "Luxury Tours"],
    highlights: [
      {
        time: "2:30",
        title: "Burj Khalifa",
        description: "Aerial view of the world's tallest building"
      },
      {
        time: "5:15",
        title: "Palm Jumeirah",
        description: "Fly over the artificial palm-shaped island"
      },
      {
        time: "8:45",
        title: "Dubai Mall",
        description: "Explore the world's largest shopping destination"
      },
      {
        time: "12:00",
        title: "Desert Safari",
        description: "Experience dune bashing and camel riding"
      }
    ],
    interactive_elements: [
      {
        time: "4:00",
        type: "info_panel",
        info: "Learn about Dubai's rapid development"
      },
      {
        time: "9:30",
        type: "hotspot",
        info: "Virtual shopping experience in Dubai Mall"
      }
    ],
    coordinates: {
      latitude: 25.2048,
      longitude: 55.2708
    },
    tags: ["luxury", "modern", "desert", "shopping", "architecture"],
    language: "English"
  },
  {
    name: "Bali Temple Journey",
    description: "Discover the spiritual beauty of Bali through its ancient temples, lush rice terraces, and vibrant Hindu culture. Experience traditional ceremonies and natural wonders.",
    country: "Indonesia",
    city: "Ubud",
    tour_type: "cultural_360",
    video_url: "https://www.youtube.com/embed/8Dse1yKGaLo",
    thumbnail: "https://images.unsplash.com/photo-1537953773345-d172ccf13cf1?w=800&h=450&fit=crop",
    duration: "13:45",
    featured: false,
    views: 8640,
    rating: 4.4,
    features: ["Temple Tours", "Rice Terraces", "Cultural Ceremonies", "Nature Walks"],
    highlights: [
      {
        time: "1:20",
        title: "Tanah Lot Temple",
        description: "Visit the iconic sea temple at sunset"
      },
      {
        time: "4:00",
        title: "Tegallalang Rice Terraces",
        description: "Walk through the stunning stepped rice fields"
      },
      {
        time: "7:30",
        title: "Ubud Monkey Forest",
        description: "Encounter playful macaques in their natural habitat"
      },
      {
        time: "10:15",
        title: "Traditional Dance",
        description: "Watch authentic Balinese Kecak fire dance"
      }
    ],
    interactive_elements: [
      {
        time: "3:00",
        type: "quiz",
        info: "Learn about Hindu-Balinese traditions"
      },
      {
        time: "8:45",
        type: "info_panel",
        info: "Discover Bali's unique irrigation system"
      }
    ],
    coordinates: {
      latitude: -8.5069,
      longitude: 115.2625
    },
    tags: ["temples", "culture", "rice-terraces", "spiritual", "nature"],
    language: "English"
  },
  {
    name: "Iceland Aurora",
    description: "Experience the otherworldly beauty of Iceland with stunning waterfalls, geysers, glaciers, and if you're lucky, the mesmerizing Northern Lights dancing across the sky.",
    country: "Iceland",
    city: "Reykjavik",
    tour_type: "360_video",
    video_url: "https://www.youtube.com/embed/TFiZE8WPUlA",
    thumbnail: "https://images.unsplash.com/photo-1539593395743-7da5ee10ff07?w=800&h=450&fit=crop",
    duration: "17:20",
    featured: false,
    views: 11250,
    rating: 4.8,
    features: ["Northern Lights", "Waterfalls", "Glaciers", "Geothermal Activity"],
    highlights: [
      {
        time: "2:45",
        title: "Gullfoss Waterfall",
        description: "Marvel at the powerful 'Golden Falls'"
      },
      {
        time: "6:00",
        title: "Geysir Hot Springs",
        description: "Watch the famous Strokkur geyser eruption"
      },
      {
        time: "9:30",
        title: "Jökulsárlón Glacier Lagoon",
        description: "See icebergs floating in the glacial lake"
      },
      {
        time: "13:45",
        title: "Northern Lights",
        description: "Experience the magical Aurora Borealis"
      }
    ],
    interactive_elements: [
      {
        time: "4:15",
        type: "info_panel",
        info: "Learn about Iceland's volcanic activity"
      },
      {
        time: "11:00",
        type: "hotspot",
        info: "Explore inside an ice cave"
      }
    ],
    coordinates: {
      latitude: 64.1466,
      longitude: -21.9426
    },
    tags: ["northern-lights", "glaciers", "waterfalls", "volcanic", "nature"],
    language: "English"
  },
  {
    name: "Machu Picchu Ancient Wonder",
    description: "Journey to the lost city of the Incas high in the Andes Mountains. Explore the mysterious ruins, learn about ancient civilizations, and enjoy breathtaking mountain vistas.",
    country: "Peru",
    city: "Cusco",
    tour_type: "interactive_360",
    video_url: "https://www.youtube.com/embed/w9c8xdQeGUs",
    thumbnail: "https://images.unsplash.com/photo-1526392060635-9d6019884377?w=800&h=450&fit=crop",
    duration: "19:15",
    featured: false,
    views: 13420,
    rating: 4.9,
    features: ["Archaeological Sites", "Mountain Views", "Historical Context", "Interactive Timeline"],
    highlights: [
      {
        time: "3:00",
        title: "Huayna Picchu",
        description: "Climb the sacred mountain for panoramic views"
      },
      {
        time: "6:45",
        title: "Temple of the Sun",
        description: "Explore the precisely carved Intihuatana stone"
      },
      {
        time: "10:20",
        title: "Agricultural Terraces",
        description: "Learn about ancient Inca farming techniques"
      },
      {
        time: "14:30",
        title: "Condor Sighting",
        description: "Spot the majestic Andean condors soaring overhead"
      }
    ],
    interactive_elements: [
      {
        time: "4:30",
        type: "quiz",
        info: "Test your knowledge of Inca civilization"
      },
      {
        time: "8:15",
        type: "navigation",
        info: "Choose between different hiking trails"
      },
      {
        time: "12:00",
        type: "info_panel",
        info: "Discover the mystery of Machu Picchu's construction"
      }
    ],
    coordinates: {
      latitude: -13.1631,
      longitude: -72.5450
    },
    tags: ["ancient", "archaeology", "mountains", "hiking", "history"],
    language: "English"
  }
];

const seedVirtualTours = async () => {
  try {
    // Connect to MongoDB
    const mongoUrl = process.env.MONGO_URL || 'mongodb://localhost:27017/advanced_travel_db';
    await mongoose.connect(mongoUrl, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    console.log('Connected to MongoDB for virtual tours seeding');
    
    // Clear existing virtual tours
    await VirtualTour.deleteMany({});
    console.log('Cleared existing virtual tours');
    
    // Insert new virtual tours
    const createdTours = await VirtualTour.insertMany(virtualToursData);
    console.log(`✅ Created ${createdTours.length} virtual tours`);
    
    // Display created tours summary
    console.log('\n📊 Virtual Tours Summary:');
    console.log('===========================');
    
    const toursByType = await VirtualTour.aggregate([
      { $group: { _id: '$tour_type', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);
    
    toursByType.forEach(type => {
      const label = type._id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
      console.log(`${label}: ${type.count} tours`);
    });
    
    const featuredCount = await VirtualTour.countDocuments({ featured: true });
    console.log(`Featured Tours: ${featuredCount}`);
    
    console.log('\n🎬 Virtual Tours Created:');
    console.log('===========================');
    createdTours.forEach(tour => {
      console.log(`${tour.name} (${tour.country}) - ${tour.tour_type} - ${tour.duration}`);
    });
    
    console.log('\n✅ Virtual tours seeding completed successfully!');
    
  } catch (error) {
    console.error('❌ Error seeding virtual tours:', error);
  } finally {
    await mongoose.connection.close();
    console.log('Database connection closed');
  }
};

// Run seeding if this file is executed directly
if (require.main === module) {
  seedVirtualTours();
}

module.exports = { seedVirtualTours, virtualToursData };