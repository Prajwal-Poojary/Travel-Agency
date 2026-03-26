# Advanced Travel Platform - Comprehensive Project Documentation

**Project Status**: Production Ready | Fully Functional | Active Development
**Stack**: Python (FastAPI), React 18, MongoDB, Google Gemini AI

---

## 📖 1. Project Overview
The Advanced Travel Platform is a full-stack, comprehensive web application designed to provide users with an immersive travel booking and exploration experience. It goes beyond standard booking platforms by integrating **360° Virtual Tours**, an **AI-powered Travel Assistant** (via Google Gemini), and dynamic filtering.

Recent major upgrades to the platform include:
- **Single Port Deployment**: Consolidation of frontend and backend to run on a single port for seamless Cloudflare Tunnel deployment and to resolve CORS issues.
- **Enhanced Communications**: Integration of Audio/Video Calling features and Meeting scheduling with "End Meeting" capabilities.
- **Dynamic Filtering**: Advanced destination filtering by price, country, and activities.

---

## 🛠️ 2. Technology Stack

### Backend
- **Framework**: Python 3.x with **FastAPI** (changed from Express.js previously).
- **Database Driver**: `motor` (Motor Asyncio for MongoDB).
- **Authentication**: `PyJWT` for token generation, `passlib` (bcrypt) for password hashing.
- **AI Integration**: `google-genai` SDK for integrating Gemini 2.5 Flash and Gemini 2.0 Flash.
- **Email Delivery**: Standard Python `smtplib` for transactional emails.
- **Concurrency**: `asyncio` for non-blocking operations.

### Frontend
- **Framework**: React 18 with modern React Hooks (`useState`, `useEffect`, `Suspense`, `lazy`).
- **Styling**: Tailwind CSS (with `@tailwindcss/forms`, `@tailwindcss/typography`). The UI heavily features modern **Glassmorphism** and dynamic particle backgrounds.
- **Animations**: Framer Motion for page transitions and micro-interactions.
- **Routing**: React Router DOM (v6).
- **State/Data Fetching**: React Query & Context API (`AuthContext`, `ThemeContext`).
- **Icons**: Lucide React.
- **Components**: Interactive UI elements such as `react-datepicker` and `react-hot-toast`.

### Database
- **Provider**: MongoDB Atlas (Cloud Database).
- **Connections**: Handled asynchronously, with an automatic fallback to in-memory Mock Data if the connection drops or is unavailable.

---

## 📂 3. Architecture & Project Structure

```text
Travel-Agency/
├── backend/                  # Python FastAPI Backend
│   ├── server.py             # Main entry point containing core APIs and logic
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Environment Variables (MONGO_URL, JWT_SECRET, GEMINI_API_KEY, etc.)
│   └── the_schema.json       # Database schema references
├── frontend/                 # React Frontend
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # Reusable UI components (Navbar, Footer, ProtectedRoute, UI/ParticleBackground, etc.)
│   │   ├── context/          # React Contexts (AuthContext, ThemeContext)
│   │   ├── pages/            # View-level components (Home, Bookings, VirtualTours, Destinations, Auth, Profile)
│   │   ├── services/         # API integration layers (e.g., api.js)
│   │   ├── App.js            # Main application router and shell
│   │   └── index.css         # Global Tailwind and custom CSS
│   └── package.json          # Node dependencies, build scripts
├── package.json              # Root package script aggregator
├── README.md                 # Brief developer readme
└── PROJECT_DOCUMENTATION.md  # Detailed project documentation (This file)
```

**Single Port Architecture Concept:**
The application is configured so the React frontend is built into `frontend/build`. The FastAPI backend detects this build folder and mounts the static files, serving `/index.html` on the root route `GET /` and catching all unmatched frontend routes via a wildcard path. This eliminates CORS complexities in production environments.

---

## 🚀 4. Core Features Deep Dive

### A. Authentication & User Profiles
- **JWT-Based Login/Register**: Users sign up with an email and password. Passwords are encrypted via bcrypt.
- **Profile Management**: Users can update their Full Name, Email, and Avatar.
- **Password Recovery**: Integrated "Forgot Password" sends a 15-minute expiring JWT link to the requested email.

### B. Destination Management & Discovery
- **Rich Browsing**: Showcases locations with pricing, categories, descriptions, images, and user ratings.
- **Advanced Filtering API**: Filtering natively supports querying by `search` text, `country`, `min_price`, `max_price`, and `activity` (e.g., Hiking, Diving, Luxury).

### C. Booking System
- **Booking Flow**: Users select check-in/out dates and guest count. The frontend calculates the total price.
- **Admin Approval**: An email is fired to the admin (`ADMIN_EMAIL`) containing one-click JWT-signed links to either **Confirm** or **Reject** the booking.
- **Booking History**: Users can view past and pending bookings in their profile dashboard. Confirmations auto-complete once the checkout date passes.

### D. Innovative Virtual Tours
- **Multimedia Integration**: Supports YouTube video IDs for 360° videos, live cams, and drone footage.
- **AI Audio Narration**: Uses **Gemini 2.0 Flash** to auto-generate a narrative travel-guide script for any given tour based on its metadata. Users can customize voice pace, duration, and tone.
- **Tour Analytics**: Tracking views and sorting by "Trending" and "Featured".
- **Favorites System**: Users can save/bookmark their favorite virtual tours securely to their profile.

### E. AI Travel Assistant (Chat Mode)
- **Persistent AI Chat**: Powered by Google Gemini. Provides recommendations and parses multi-turn travel conversations.
- **Chat History**: Sessions are saved securely per user in MongoDB so past conversations can be resumed or deleted at any point.
- **Structured Recommendations**: A secondary endpoint parses user preferences (budget, style, duration) to return structured JSON recommendations directly from the LLM.

### F. Communication & Meetings Features
- **Calling**: Audio/Video capabilities accessible from the user interface InfoPanels.
- **Meeting End Control**: Custom-built host features ensuring meetings persist uniquely until explicitly terminated by the host, maintaining organized schedules.

---

## 🌐 5. API Master Reference (FastAPI Routes)

All routes below require a standard Bearer `JWT` token mapped to the `Authorization` header unless public.

### System & Health
- `GET /` — Serves React application in production mode.
- `GET /api/health` — Returns status of Database and Gemini API.

### Auth & User Profile
- `POST /api/auth/register` — Creates a new account.
- `POST /api/auth/login` — Authenticates and returns JWT.
- `GET /api/auth/profile` — Retrieves the authenticated user profile.
- `PUT /api/auth/profile` — Modifies user profile data.
- `POST /api/auth/forgot-password` — Dispatches reset email.
- `POST /api/auth/reset-password` — Consumes reset token and modifies password.

### Destinations
- `GET /api/destinations` — Fetches destinations (Params: `search`, `country`, `min_price`, `max_price`, `activity`).
- `GET /api/destinations/featured` — Fetches top highlighted features.
- `GET /api/destinations/countries`
- `GET /api/destinations/activities`
- `GET /api/destinations/{destination_id}` — Get single location.
- `POST /api/destinations` — Creates a new destination (Admin mock logic).

### Virtual Tours
- `GET /api/virtual-tours` — Fetches interactive tours with pagination.
- `GET /api/virtual-tours/featured`
- `GET /api/virtual-tours/trending`
- `GET /api/virtual-tours/{tour_id}`
- `POST /api/virtual-tours/{tour_id}/view` — Increments the view counter.
- `GET /api/virtual-tours/favorites` — Lists currently authenticated user's saved tours.
- `POST /api/virtual-tours/{tour_id}/favorite` — Adds tour to favorites.
- `DELETE /api/virtual-tours/{tour_id}/favorite` — Removes from favorites.
- `POST /api/virtual-tours/{tour_id}/narrate` — Dynamically generates an AI audio narration script via Gemini.

### Bookings & Reviews
- `POST /api/bookings` — Request a booking (Triggers Admin email).
- `GET /api/bookings` — Fetch all bookings for the authenticated user.
- `GET /api/bookings/confirm` — (Admin only) Approves via JWT link.
- `GET /api/bookings/reject` — (Admin only) Cancels via JWT link.
- `DELETE /api/bookings/{booking_id}` — User cancellation.
- `POST /api/reviews` — Creates a review for a destination.
- `GET /api/reviews/{destination_id}` — Lists reviews per destination.
- `DELETE /api/reviews/{review_id}` — Deletes review.

### AI Chat
- `GET /api/chat/sessions` — Lists all previous user chat threads.
- `GET /api/chat/sessions/{session_id}` — Recovers a specific chat log.
- `DELETE /api/chat/sessions/{session_id}` — Wipes history for thread.
- `POST /api/chat` — Send a message to the Gemini AI and receive response.
- `POST /api/ai/recommendations` — Bullet-point specific travel itinerary generation tool.

---

## 🗄️ 6. Database Schema Design
The MongoDB database relies heavily on the `motor` asynchronous driver. Important collections include:

1. **users**: Tracks `{ user_id, username, email, password (hashed), avatar, created_at }`. Indexed natively.
2. **destinations**: Contains fields for `{ destination_id, name, description, country, price, rating, activities[], featured, images[] }`.
3. **virtual_tours**: Handles `{ tour_id, name, duration, tour_type, video_url, views, features[], highlights[] }`.
4. **chat_sessions**: Persists arrays of `{ role, content, timestamp }` structured uniquely by `{ session_id, user_id }`.
5. **bookings**: Resolves user transactions mapping `{ booking_id, user_id, destination_id, check_in_date, check_out_date, status, total_price }`.
6. **favorites**: Contains `{ user_id, tour_id, created_at }`. Acts as a junction lookup collection.
7. **reviews**: User feedback `{ review_id, destination_id, rating, comment }`.

*Note: In the event of an Atlas failure or missing environment configurations, `server.py` implements a robust "fallback mode" that temporarily swaps to in-memory MOCK_DATA logic to ensure the frontend still loads beautifully for demos.*

---

## 🚀 7. Deployment Instructions

### Local Development Environment
1. Traverse into `/backend` and create a `.env` file (this file is ignored by Git for security) configuring `MONGO_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`.
2. Ensure you have the corresponding frontend `.env` or point proxy to `http://localhost:8001`.
3. In Root Directory: `npm run install-all`.
4. Start both servers concurrently: `npm start`.

### Production Build / Cloudflare Tunnel
Because the backend includes logic to natively serve the compiled React JS bundles statically, deployments are drastically simplified.

1. Configure `.env` on production server.
2. Build the React frontend: `cd frontend && npm run build`
3. Execute `npm run start:prod` (Typically using `uvicorn server:app --host 0.0.0.0 --port 8001`).
4. Apply the single exposed `8001` port to a Cloudflare tunnel or NGINX reverse proxy. All API calls execute natively against the same origin host footprint, bypassing CORS checks completely!

---
*Generated by Antigravity on behalf of Project Team.*
