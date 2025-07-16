const express = require('express');
const { body, validationResult } = require('express-validator');
const ChatSession = require('../models/ChatSession');
const auth = require('../middleware/auth');

const router = express.Router();

// Google Gemini AI setup
let genAI = null;
let model = null;

try {
  if (process.env.GEMINI_API_KEY) {
    const { GoogleGenerativeAI } = require('@google/generative-ai');
    genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    console.log('Google Gemini AI initialized successfully');
  } else {
    console.log('GEMINI_API_KEY not found in environment variables');
  }
} catch (error) {
  console.log('Google Gemini AI initialization failed:', error.message);
}

// AI service functions
const getAIRecommendations = async (userPreferences, context = '') => {
  if (!model) {
    return { 
      error: 'AI service not configured',
      recommendations: 'AI travel recommendations are currently unavailable. Please configure your API key to enable this feature.'
    };
  }
  
  try {
    const prompt = `
    You are an expert travel advisor. Based on the following user preferences, provide personalized travel recommendations:
    
    User Preferences: ${JSON.stringify(userPreferences)}
    Context: ${context}
    
    Please provide:
    1. Top 3 destination recommendations with reasons
    2. Best time to visit each destination
    3. Suggested activities for each destination
    4. Budget estimates
    5. Travel tips specific to the user's preferences
    
    Format your response as a structured, helpful travel guide.
    `;
    
    const result = await model.generateContent(prompt);
    const response = await result.response;
    
    return {
      recommendations: response.text()
    };
  } catch (error) {
    console.error('AI recommendation error:', error);
    return { 
      error: 'AI service temporarily unavailable',
      recommendations: 'We apologize, but our AI travel assistant is currently experiencing technical difficulties. Please try again later.'
    };
  }
};

const generateAIResponse = async (message, chatHistory = []) => {
  if (!model) {
    return 'I apologize, but the AI chat service is currently unavailable. Our AI travel assistant requires proper API configuration to function. Please contact support for assistance.';
  }
  
  try {
    const context = `You are a helpful travel assistant. You help users plan their trips, provide destination recommendations, travel tips, and answer travel-related questions. Be friendly, informative, and concise.`;
    
    // Include chat history for context
    let conversationContext = '';
    if (chatHistory.length > 0) {
      conversationContext = '\n\nPrevious conversation:\n' + 
        chatHistory.slice(-5).map(msg => `${msg.role}: ${msg.content}`).join('\n');
    }
    
    const fullPrompt = `${context}${conversationContext}\n\nUser: ${message}\n\nAssistant:`;
    
    const result = await model.generateContent(fullPrompt);
    const response = await result.response;
    
    return response.text();
  } catch (error) {
    console.error('AI chat error:', error);
    return 'I apologize, but I\'m experiencing technical difficulties right now. Please try again in a few moments, or contact our support team if the issue persists.';
  }
};

// @route   POST /api/chat
// @desc    Chat with AI assistant
// @access  Public
router.post('/', [
  body('message').isLength({ min: 1, max: 1000 }),
  body('session_id').optional().isString()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { message, session_id } = req.body;
    
    // Get or create chat session
    let chatSession = null;
    if (session_id) {
      chatSession = await ChatSession.findOne({ session_id });
    }
    
    if (!chatSession) {
      chatSession = new ChatSession({
        session_id: session_id || undefined,
        messages: []
      });
    }
    
    // Add user message to history
    chatSession.messages.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    });
    
    // Generate AI response
    const aiResponse = await generateAIResponse(message, chatSession.messages);
    
    // Add AI response to history
    chatSession.messages.push({
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date()
    });
    
    // Save chat session
    await chatSession.save();
    
    res.json({
      session_id: chatSession.session_id,
      response: aiResponse,
      timestamp: new Date()
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Chat service temporarily unavailable',
      response: 'I apologize, but our chat service is currently experiencing issues. Please try again later.'
    });
  }
});

// @route   GET /api/chat/sessions/:session_id
// @desc    Get chat session history
// @access  Public
router.get('/sessions/:session_id', async (req, res) => {
  try {
    const { session_id } = req.params;
    
    const chatSession = await ChatSession.findOne({ session_id });
    
    if (!chatSession) {
      return res.status(404).json({ error: 'Chat session not found' });
    }
    
    res.json(chatSession);
  } catch (error) {
    console.error('Get chat session error:', error);
    res.status(500).json({ error: 'Server error fetching chat session' });
  }
});

// @route   DELETE /api/chat/sessions/:session_id
// @desc    Clear chat session
// @access  Public
router.delete('/sessions/:session_id', async (req, res) => {
  try {
    const { session_id } = req.params;
    
    await ChatSession.findOneAndDelete({ session_id });
    
    res.json({ message: 'Chat session cleared successfully' });
  } catch (error) {
    console.error('Clear chat session error:', error);
    res.status(500).json({ error: 'Server error clearing chat session' });
  }
});

// @route   POST /api/chat/recommendations
// @desc    Get AI travel recommendations
// @access  Private
router.post('/recommendations', auth, [
  body('preferences').isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { preferences } = req.body;
    const context = `User: ${req.user.username}, Email: ${req.user.email}`;
    
    const recommendations = await getAIRecommendations(preferences, context);
    
    res.json(recommendations);
  } catch (error) {
    console.error('AI recommendations error:', error);
    res.status(500).json({ 
      error: 'Recommendation service temporarily unavailable',
      recommendations: 'Unable to generate recommendations at this time. Please try again later.'
    });
  }
});

module.exports = router;