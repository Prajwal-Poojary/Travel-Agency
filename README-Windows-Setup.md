# Advanced Travel Platform - Windows Setup Guide

## Prerequisites

Before setting up the project on Windows, ensure you have the following installed:

### Required Software:
1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

2. **Git** (optional, for version control)
   - Download from: https://git-scm.com/

3. **MongoDB** (optional, for local database)
   - Download from: https://www.mongodb.com/try/download/community
   - Or use the cloud MongoDB (recommended for development)

### Optional but Recommended:
- **VS Code** or your preferred code editor
- **Postman** or similar tool for API testing

## Project Setup

### 1. Clone or Download the Project
```bash
# If using Git
git clone <repository-url>
cd advanced-travel-platform

# Or download and extract the ZIP file
```

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Install dependencies:
```bash
npm install
```

Setup environment variables:
```bash
# Copy the local environment file
copy .env.local .env

# Edit .env file with your preferred text editor
# Update API keys if needed
```

Seed the database (if using cloud MongoDB):
```bash
npm run seed
```

Start the backend server:
```bash
# For development with auto-restart
npm run dev

# Or for production mode
npm start
```

The backend will be running on: `http://localhost:8001`

### 3. Frontend Setup

Open a new terminal window and navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Setup environment variables:
```bash
# Copy the local environment file
copy .env.local .env

# Edit .env file if needed
```

Start the frontend server:
```bash
npm start
```

The frontend will be running on: `http://localhost:3000`

## API Keys Required

To unlock full functionality, you'll need to obtain the following API keys:

### 1. Google Gemini API Key (for AI Assistant)
- Go to: https://makersuite.google.com/app/apikey
- Create a new API key
- Update `GEMINI_API_KEY` in backend/.env

### 2. OpenWeatherMap API Key (for Weather Data)
- Go to: https://openweathermap.org/api
- Sign up and get a free API key
- Update `WEATHER_API_KEY` in backend/.env

### 3. MapBox Token (for Maps)
- Go to: https://www.mapbox.com/
- Sign up and get an access token
- Update `REACT_APP_MAPBOX_TOKEN` in frontend/.env

## Database Options

### Option 1: Cloud MongoDB (Recommended)
- The project is pre-configured to use MongoDB Atlas
- No additional setup required
- Database is already seeded with sample data

### Option 2: Local MongoDB
- Install MongoDB Community Server
- Start MongoDB service
- Update `MONGO_URL` in backend/.env to: `mongodb://localhost:27017/advanced_travel_db`
- Run: `npm run seed` to populate with sample data

## Testing the Setup

### Backend API Testing:
1. Open your browser to: `http://localhost:8001/api/health`
2. You should see: `{"status":"healthy",...}`
3. Test destinations: `http://localhost:8001/api/destinations`

### Frontend Testing:
1. Open your browser to: `http://localhost:3000`
2. You should see the beautiful homepage
3. Test navigation to different pages
4. Try the AI Assistant (if Gemini API key is configured)

## Common Issues and Solutions

### Issue 1: "npm not found"
- **Solution**: Install Node.js from nodejs.org
- Restart your terminal after installation

### Issue 2: "Port already in use"
- **Solution**: 
  - Change the port in backend/.env: `PORT=8002`
  - Or kill the process using the port: `netstat -ano | findstr :8001`

### Issue 3: "MongoDB connection failed"
- **Solution**: 
  - Check your internet connection for cloud MongoDB
  - For local MongoDB, ensure the service is running
  - Verify the MONGO_URL in backend/.env

### Issue 4: "CORS errors"
- **Solution**: 
  - Make sure CORS_ORIGINS in backend/.env includes your frontend URL
  - Current setting: `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

### Issue 5: "Dependencies installation failed"
- **Solution**: 
  - Clear npm cache: `npm cache clean --force`
  - Delete node_modules and package-lock.json, then run `npm install` again

## Development Scripts

### Backend Scripts:
```bash
npm start          # Start the server
npm run dev        # Start with auto-restart (nodemon)
npm run seed       # Seed the database with sample data
npm test           # Run tests
```

### Frontend Scripts:
```bash
npm start          # Start the development server
npm run build      # Build for production
npm test           # Run tests
```

## Project Structure

```
advanced-travel-platform/
├── backend/                 # Node.js Express backend
│   ├── models/             # MongoDB schemas
│   ├── routes/             # API routes
│   ├── middleware/         # Authentication & utilities
│   ├── seeds/              # Database seeding
│   ├── server.js           # Main server file
│   ├── package.json        # Dependencies
│   └── .env                # Environment variables
├── frontend/               # React frontend
│   ├── src/                # React components
│   ├── public/             # Static assets
│   ├── package.json        # Dependencies
│   └── .env                # Environment variables
└── README-Windows-Setup.md # This file
```

## Features Available

### ✅ Working Features:
- User authentication (register/login)
- Destination browsing and search
- Booking system
- Review and rating system
- AI-powered travel assistant
- Virtual tours interface
- Real-time features with WebSocket
- Beautiful responsive UI

### 🔧 Requires API Keys:
- Weather data (OpenWeatherMap)
- AI assistant (Google Gemini)
- Interactive maps (MapBox)

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure API keys are properly configured
4. Check the console for detailed error messages

## Production Deployment

For production deployment:
1. Set `NODE_ENV=production` in backend/.env
2. Build the frontend: `npm run build` in frontend/
3. Configure proper production URLs
4. Set up SSL certificates
5. Use PM2 or similar for process management

---

**Happy Coding! 🚀**