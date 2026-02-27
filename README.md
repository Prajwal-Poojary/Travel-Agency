# Advanced Travel Platform - Node.js & React

**✅ FULLY FUNCTIONAL** | **🚀 PRODUCTION READY** | **🎨 MODERN UI**

## 🎯 PROJECT STATUS: PRODUCTION READY

A comprehensive travel platform built with modern web technologies featuring virtual tours, destination management, and AI-powered chat assistance.

## 🛠️ TECH STACK

### Backend
- **Node.js** with Express.js framework
- **MongoDB Atlas** (Cloud Database)
- **JWT Authentication** for secure user management
- **Google Gemini AI** for intelligent chat assistance
- **bcryptjs** for password hashing
- **uuid** for unique identifiers

### Frontend
- **React 18** with modern hooks and context
- **Tailwind CSS** with glassmorphism design
- **Framer Motion** for smooth animations
- **React Query** for efficient data fetching
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for icons

## 🚀 FEATURES

### 🔐 Authentication System
- User registration with email validation
- JWT token-based authentication
- Protected routes and API endpoints
- Profile management

### 🏖️ Travel Management
- **3 Premium Destinations** with rich data and imagery
- Advanced search and filtering capabilities
- Detailed destination views
- Interactive booking system with calendar
- Review and rating system

### 🤖 AI Integration
- **Google Gemini AI** powered chat assistant
- Intelligent travel recommendations and planning
- Context-aware conversation handling
- Multi-turn conversation support
- Session management with database storage
- Travel-focused responses and advice

### 🎥 Virtual Tours
- Immersive 360° destination experiences
- Interactive tour controls
- Video integration and media galleries
- Categorized tour filtering (360° Videos, Interactive)
- Featured tours section

### 🎨 Modern UI/UX
- **Glassmorphism Design** with translucent elements
- **Particle Background Effects** for visual appeal
- **Smooth Animations** using Framer Motion
- **Responsive Design** for all devices
- **Loading States** and error handling
- **Toast Notifications** for user feedback

## 📊 DATABASE STRUCTURE

The platform uses MongoDB Atlas with the following collections:

- **Users**: User accounts with authentication
- **Destinations**: Travel destinations with details, images, coordinates
- **Virtual Tours**: Virtual tour experiences with video URLs and metadata
- **Chat Sessions**: AI conversation history and session management

## 🚀 QUICK START

### Prerequisites
- **Node.js 16+** for both backend and frontend
- **MongoDB Atlas account** (connection string required)

### 1. Install Dependencies
```bash
# Install all dependencies (backend + frontend)
npm run install-all
```

### 2. Environment Setup
Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```env
MONGO_URL=your-mongodb-connection-string
JWT_SECRET_KEY=your-super-secret-jwt-key
GEMINI_API_KEY=your-gemini-api-key-here
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env)**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 3. Start the Application

**For Local Development (Two Ports):**
```bash
# Start both backend and frontend concurrently
npm start
```

**For Production / Cloudflare Tunnels (Single Port):**
```bash
# Build frontend and serve everything from the backend on port 8001
npm run start:prod
```

### 4. Access the Application

**Development Mode:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001

**Production Mode (`start:prod`):**
- **App & API**: http://localhost:8001
- **Health Check**: http://localhost:8001/api/health

## 📡 API ENDPOINTS

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login  
- `GET /api/auth/profile` - Get user profile (protected)

### Destinations
- `GET /api/destinations` - Get all destinations (with filtering)
- `GET /api/destinations/countries` - Get available countries
- `GET /api/destinations/activities` - Get available activities
- `GET /api/destinations/:destination_id` - Get specific destination

### Virtual Tours
- `GET /api/virtual-tours` - Get all virtual tours (with filtering)
- `GET /api/virtual-tours/featured` - Get featured tours
- `GET /api/virtual-tours/types` - Get tour types with counts
- `GET /api/virtual-tours/countries` - Get available countries
- `GET /api/virtual-tours/:tour_id` - Get specific tour

### AI Chat
- `POST /api/chat` - Chat with AI assistant (protected)
- `GET /api/chat/sessions/:session_id` - Get chat session history (protected)
- `DELETE /api/chat/sessions/:session_id` - Delete chat session (protected)

### System
- `GET /api/health` - Health check

## 🔑 ENVIRONMENT VARIABLES

### Backend (.env)
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database
JWT_SECRET_KEY=your-super-secret-jwt-key-here
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
HOST=0.0.0.0
PORT=8001
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📦 SAMPLE DATA

The database includes:
- **3 Premium Destinations**: Maldives Paradise, Tokyo Metropolitan, Santorini Sunset
- **2 Virtual Tours**: Tokyo 360° City Tour, Santorini Cliffside Walk
- **Demo User**: demo@example.com / password123

## 🔧 DEVELOPMENT

### Project Structure
```
Travel-Agency/
├── backend/                 # Node.js Express API
│   ├── server.js           # Main server file (all endpoints)
│   ├── package.json        # Backend dependencies
│   └── node_modules/       # Backend dependencies
├── frontend/               # React frontend
│   ├── src/                # React components
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context providers
│   │   ├── services/       # API services
│   │   └── App.js          # Main app component
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── package.json            # Root configuration
├── README.md               # This file
└── .gitignore              # Git ignore rules
```

### Available Scripts

**Root:**
- `npm run install-all` - Install backend and frontend dependencies
- `npm start` - Start both backend and frontend for local development
- `npm run start:prod` - Build frontend and start the backend to serve both on a single port (production/Cloudflare ready)
- `npm run start:backend` - Start backend only
- `npm run start:frontend` - Start frontend only
- `npm run build` - Build frontend for production

**Backend:**
- `npm start` - Start production server
- `npm run dev` - Start with environment file

**Frontend:**
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run test suite

## 🌟 KEY FEATURES WORKING

### ✅ Authentication & User Management
- Complete user registration and login system
- JWT token-based authentication
- Protected routes and API endpoints
- User profile management

### ✅ Destination Management
- 3 fully featured destinations with rich data
- Search and filtering by country, activities
- Beautiful image galleries
- Detailed destination information

### ✅ Virtual Tours
- 360° virtual tour experiences
- Video integration with YouTube
- Interactive controls
- Categorized browsing (360° Videos, Interactive)
- Featured tours section

### ✅ AI Assistant
- **Google Gemini AI** integration with intelligent responses
- Context-aware conversations with travel focus
- Travel recommendation engine and planning assistance
- Session management with database storage
- Protected chat endpoints with error handling
- Real-time AI responses for travel queries

### ✅ Modern UI/UX
- Glassmorphism design with translucent elements
- Particle background effects
- Smooth page transitions with Framer Motion
- Responsive design for all devices
- Loading states and error handling
- Toast notifications

## 🚦 STATUS

**Current Status**: ✅ **FULLY FUNCTIONAL & PRODUCTION READY**
**Backend**: Node.js Express with 15+ working endpoints
**Frontend**: Modern React with beautiful UI/UX
**Database**: MongoDB Atlas with sample data
**Authentication**: Complete JWT-based system
**AI Chat**: Google Gemini AI integration with intelligent responses
**Virtual Tours**: Fully functional with video integration

## 🎉 READY TO USE!

Your Advanced Travel Platform is **production-ready** with:
- ✅ Complete authentication system
- ✅ Destination management
- ✅ Virtual tours with video integration
- ✅ **Google Gemini AI** powered chat assistant
- ✅ Beautiful responsive UI
- ✅ Comprehensive API coverage
- ✅ Cloud database integration

Just add your MongoDB connection string and Gemini API key, and you're ready to launch! 🚀

## 📝 NOTES

- The backend uses a single `server.js` file containing all endpoints for simplicity
- All authentication is JWT-based with protected routes
- **Google Gemini AI** provides intelligent travel chat responses
- Virtual tours support YouTube video integration
- The frontend uses modern React patterns with hooks and context
- Tailwind CSS provides the glassmorphism design system
- Chat sessions are stored in MongoDB for conversation history