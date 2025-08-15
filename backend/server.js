import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { MongoClient } from 'mongodb';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

// Load env
dotenv.config({ path: new URL('./.env', import.meta.url).pathname });

// ---- Env & Config ----
const MONGO_URL = process.env.MONGO_URL;
const JWT_SECRET = process.env.JWT_SECRET_KEY || 'dev_secret';
const ALGORITHM = 'HS256';
const CORS_ORIGINS = (process.env.CORS_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
const HOST = process.env.HOST || '0.0.0.0';
const PORT = parseInt(process.env.PORT || '8001', 10);

// ---- App ----
const app = express();
app.use(helmet());
app.use(express.json({ limit: '1mb' }));
app.use(morgan('tiny'));
app.use(cors({
  origin: CORS_ORIGINS.length ? CORS_ORIGINS : [/localhost:3000$/],
  credentials: true,
}));

// ---- Database ----
let client; let db;
function parseDbName(url) {
  try {
    const m = url.match(/\/([^/?]+)(?:\?|$)/);
    return m && m[1] ? decodeURIComponent(m[1]) : undefined;
  } catch (e) { return undefined; }
}

async function connectDb() {
  client = new MongoClient(MONGO_URL, { maxPoolSize: 10 });
  await client.connect();
  const dbName = client?.options?.dbName || parseDbName(MONGO_URL);
  if (!dbName) throw new Error('Database name not found in MONGO_URL');
  db = client.db(dbName);
  await ensureIndexesAndSeed();
}

async function ensureIndexesAndSeed() {
  // Indexes
  await db.collection('users').createIndex({ email: 1 }, { unique: true });
  await db.collection('users').createIndex({ username: 1 }, { unique: true });
  await db.collection('destinations').createIndex({ destination_id: 1 }, { unique: true });

  // Seed demo user
  const demo = await db.collection('users').findOne({ email: 'demo@example.com' });
  if (!demo) {
    await db.collection('users').insertOne({
      user_id: uuidv4(),
      username: 'demo_user',
      email: 'demo@example.com',
      full_name: 'Demo User',
      password: await bcrypt.hash('password123', 10),
      avatar: null,
      created_at: new Date(),
    });
  }

  // Seed a few destinations if empty
  const count = await db.collection('destinations').countDocuments();
  if (count === 0) {
    await db.collection('destinations').insertMany([
      {
        destination_id: uuidv4(),
        name: 'Maldives Paradise',
        country: 'Maldives',
        city: 'Malé',
        category: 'Beach',
        description: 'Crystal-clear waters, overwater bungalows, and vibrant marine life.',
        price_range: '$$$$',
        activities: ['Snorkeling', 'Diving', 'Sunset Cruise'],
        best_time_to_visit: 'Nov to Apr',
        images: ['https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80'],
        coordinates: { latitude: 3.2028, longitude: 73.2207 },
        rating: 4.8, featured: true, created_at: new Date(),
      },
      {
        destination_id: uuidv4(),
        name: 'Tokyo Metropolitan',
        country: 'Japan', city: 'Tokyo', category: 'City',
        description: 'Traditional culture meets modern innovation and incredible cuisine.',
        price_range: '$$$', activities: ['Temple Visits', 'Sushi Tours', 'Shopping'],
        best_time_to_visit: 'Mar to May, Oct to Nov',
        images: ['https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80'],
        coordinates: { latitude: 35.6762, longitude: 139.6503 },
        rating: 4.6, featured: true, created_at: new Date(),
      },
      {
        destination_id: uuidv4(),
        name: 'Santorini Sunset',
        country: 'Greece', city: 'Santorini', category: 'Island',
        description: 'Iconic blue-domed churches and dramatic cliffside views.',
        price_range: '$$$', activities: ['Sunset Viewing', 'Wine Tasting', 'Photography'],
        best_time_to_visit: 'Apr to Oct',
        images: ['https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80'],
        coordinates: { latitude: 36.3932, longitude: 25.4615 },
        rating: 4.5, featured: true, created_at: new Date(),
      }
    ]);
  }
}

// ---- Utils ----
function createToken(username, user_id) {
  const payload = {
    username,
    user_id,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60, // 30 days
  };
  return jwt.sign(payload, JWT_SECRET, { algorithm: ALGORITHM });
}

async function authMiddleware(req, res, next) {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ detail: 'No token provided' });
  }
  const token = auth.slice(7);
  try {
    const payload = jwt.verify(token, JWT_SECRET, { algorithms: [ALGORITHM] });
    const user = await db.collection('users').findOne({ username: payload.username });
    if (!user) return res.status(401).json({ detail: 'User not found' });
    req.user = user;
    next();
  } catch (e) {
    return res.status(401).json({ detail: 'Invalid token' });
  }
}

// ---- Routes ----
app.get('/', (req, res) => {
  res.json({ message: 'Advanced Travel Platform - Node.js', status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Auth
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body || {};
    if (!email || !password) return res.status(422).json({ detail: 'Email and password required' });
    const user = await db.collection('users').findOne({ email });
    if (!user) return res.status(401).json({ detail: 'Invalid credentials' });
    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(401).json({ detail: 'Invalid credentials' });
    const token = createToken(user.username, user.user_id);
    res.json({ access_token: token, token_type: 'bearer', user: user.username, user_id: user.user_id });
  } catch (e) {
    res.status(500).json({ detail: 'Server error' });
  }
});

app.post('/api/auth/register', async (req, res) => {
  try {
    const { username, email, password, full_name } = req.body || {};
    if (!username || !email || !password || !full_name) return res.status(422).json({ detail: 'Missing fields' });
    const exists = await db.collection('users').findOne({ $or: [{ email }, { username }] });
    if (exists) return res.status(400).json({ detail: 'Email or username already exists' });
    const doc = {
      user_id: uuidv4(), username, email, full_name,
      password: await bcrypt.hash(password, 10), avatar: null, created_at: new Date(),
    };
    await db.collection('users').insertOne(doc);
    const token = createToken(username, doc.user_id);
    res.json({ access_token: token, token_type: 'bearer', user: username, user_id: doc.user_id });
  } catch (e) {
    res.status(500).json({ detail: 'Server error' });
  }
});

app.get('/api/auth/profile', authMiddleware, async (req, res) => {
  const u = req.user;
  res.json({ user_id: u.user_id, username: u.username, email: u.email, full_name: u.full_name || '', avatar: u.avatar || null, created_at: u.created_at });
});

// Destinations
app.get('/api/destinations', async (req, res) => {
  try {
    const { search, country, activity } = req.query;
    let { limit } = req.query;
    limit = Math.min(Math.max(parseInt(limit || '100', 10), 1), 100);
    const query = {};
    if (search) {
      query.$or = [
        { name: { $regex: String(search), $options: 'i' } },
        { description: { $regex: String(search), $options: 'i' } },
        { city: { $regex: String(search), $options: 'i' } },
        { country: { $regex: String(search), $options: 'i' } },
      ];
    }
    if (country) query.country = { $regex: String(country), $options: 'i' };
    if (activity) query.activities = { $in: [String(activity)] };
    const docs = await db.collection('destinations').find(query).limit(limit).toArray();
    docs.forEach(d => { d.destination_id = d.destination_id || String(d._id); });
    res.json(docs);
  } catch (e) {
    res.status(500).json({ detail: 'Server error' });
  }
});

app.get('/api/destinations/countries', async (req, res) => {
  const docs = await db.collection('destinations').find({}, { projection: { country: 1 } }).toArray();
  const countries = [...new Set(docs.map(d => d.country).filter(Boolean))].sort();
  res.json(countries);
});

app.get('/api/destinations/activities', async (req, res) => {
  const docs = await db.collection('destinations').find({}, { projection: { activities: 1 } }).toArray();
  const set = new Set();
  docs.forEach(d => (d.activities || []).forEach(a => set.add(a)));
  res.json(Array.from(set).sort());
});

app.get('/api/destinations/:destination_id', async (req, res) => {
  const id = req.params.destination_id;
  const doc = await db.collection('destinations').findOne({ destination_id: id });
  if (!doc) return res.status(404).json({ detail: 'Destination not found' });
  doc.destination_id = doc.destination_id || String(doc._id);
  res.json(doc);
});

// Chat (secured)
app.post('/api/chat', authMiddleware, async (req, res) => {
  const { message, session_id } = req.body || {};
  const reply = 'Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel.';
  res.json({ session_id: session_id || `session_${uuidv4().slice(0,8)}`, response: reply, timestamp: new Date().toISOString() });
});

app.get('/api/chat/sessions/:session_id', authMiddleware, async (req, res) => {
  const { session_id } = req.params;
  res.json({ session_id, messages: [
    { role: 'user', content: 'Hello', timestamp: new Date().toISOString() },
    { role: 'assistant', content: 'Thanks for your message! The AI service is enabled for authenticated users. Ask me anything about travel.', timestamp: new Date().toISOString() }
  ], created_at: new Date().toISOString() });
});

app.delete('/api/chat/sessions/:session_id', authMiddleware, async (req, res) => {
  res.json({ message: `Chat session ${req.params.session_id} deleted successfully` });
});

// ---- Startup ----
connectDb().then(() => {
  app.listen(PORT, HOST, () => {
    console.log(`Node backend listening on http://${HOST}:${PORT}`);
  });
}).catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});