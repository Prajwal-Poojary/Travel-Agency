import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  Send, 
  Sparkles, 
  MessageCircle, 
  User, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Download, 
  Share2, 
  RefreshCw, 
  Settings, 
  Star, 
  MapPin, 
  Calendar, 
  DollarSign, 
  Plane, 
  Camera, 
  Heart, 
  TrendingUp,
  Zap,
  Globe,
  Clock,
  Users
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useMutation } from 'react-query';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';

const SESSION_STORAGE_KEY = 'ai_session_id';

const EnhancedAIAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [userPreferences, setUserPreferences] = useState({
    budget: 'moderate',
    activities: [],
    travel_style: 'leisure',
    duration: '1 week',
    group_size: 2,
    interests: []
  });
  
  const { isAuthenticated, user } = useAuth();
  const messagesEndRef = useRef(null);
  const speechRecognition = useRef(null);
  const speechSynthesis = useRef(null);

  // helpers
  const generateSessionId = () => 'session_' + Math.random().toString(36).substr(2, 9);

  const loadOrCreateSession = () => {
    let sid = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!sid) {
      sid = generateSessionId();
      localStorage.setItem(SESSION_STORAGE_KEY, sid);
    }
    setSessionId(sid);
    return sid;
  };

  // Initialize AI session and try loading history
  useEffect(() => {
    const sid = loadOrCreateSession();

    const initialMessage = {
      type: 'assistant',
      content: `Hello${user ? ` ${user.username}` : ''}! I'm your AI travel assistant powered by advanced AI technology. I can help you:\n\n🌍 **Discover Destinations** - Find perfect places based on your preferences\n✈️ **Plan Trips** - Create detailed itineraries and travel plans  \n💰 **Budget Planning** - Get cost estimates and money-saving tips\n🎯 **Personalized Recommendations** - Tailored suggestions just for you\n📅 **Best Times to Visit** - Optimal travel timing advice\n🏨 **Accommodation & Activities** - Find the best places to stay and things to do\n\nWhat would you like to explore today?`,
      timestamp: new Date(),
      suggestions: [
        'Find me a romantic destination for honeymoon',
        'Plan a family trip to Europe',
        'Budget-friendly destinations in Asia',
        'Adventure activities in New Zealand'
      ]
    };
    setMessages([initialMessage]);

    // Fetch session history if authenticated
    if (isAuthenticated && sid) {
      apiService.getChatSession(sid).then(data => {
        if (data?.messages?.length) {
          const history = data.messages.map(m => ({
            type: m.role === 'user' ? 'user' : 'assistant',
            content: m.content,
            timestamp: new Date(m.timestamp)
          }));
          setMessages(prev => [initialMessage, ...history]);
        }
      }).catch(() => {});
    }
  }, [user, isAuthenticated]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      speechRecognition.current = new window.webkitSpeechRecognition();
      speechRecognition.current.continuous = false;
      speechRecognition.current.interimResults = false;
      speechRecognition.current.lang = 'en-US';
      speechRecognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };
      speechRecognition.current.onerror = () => {
        setIsListening(false);
        toast.error('Speech recognition error');
      };
    }
    if ('speechSynthesis' in window) {
      speechSynthesis.current = window.speechSynthesis;
    }
  }, []);

  // Chat mutation
  const chatMutation = useMutation(
    (message) => apiService.chatWithAI({ message, session_id: sessionId }),
    {
      onSuccess: (data) => {
        const aiMessage = {
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          sessionId: data.session_id
        };
        // ensure we keep server session id
        if (data.session_id && data.session_id !== sessionId) {
          localStorage.setItem(SESSION_STORAGE_KEY, data.session_id);
          setSessionId(data.session_id);
        }
        setMessages(prev => [...prev, aiMessage]);

        if (isSpeaking && speechSynthesis.current) {
          const utterance = new SpeechSynthesisUtterance(data.response);
          speechSynthesis.current.speak(utterance);
        }
      },
      onError: () => {
        toast.error('Failed to get AI response');
        const errorMessage = {
          type: 'assistant',
          content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
          timestamp: new Date(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      },
      onSettled: () => setIsLoading(false)
    }
  );

  // Recommendations mutation with support for array results
  const recommendationsMutation = useMutation(
    (preferences) => apiService.getAIRecommendations(preferences),
    {
      onSuccess: (data) => {
        if (data?.recommendations) {
          const recs = data.recommendations;
          const msg = {
            type: 'assistant',
            content: 'Based on your preferences, here are my personalized recommendations:',
            timestamp: new Date(),
          };
          if (Array.isArray(recs)) {
            msg.recommendationsList = recs;
          } else {
            msg.recommendations = recs; // backward compatibility
          }
          setMessages(prev => [...prev, msg]);
        }
      },
      onError: () => toast.error('Failed to get recommendations')
    }
  );

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim()) return;

    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    chatMutation.mutate(messageText);
  };

  const handleSuggestionClick = (suggestion) => handleSendMessage(suggestion);

  const handleVoiceInput = () => {
    if (!speechRecognition.current) {
      toast.error('Speech recognition not supported');
      return;
    }
    if (isListening) {
      speechRecognition.current.stop();
      setIsListening(false);
    } else {
      speechRecognition.current.start();
      setIsListening(true);
    }
  };

  const toggleSpeech = () => {
    setIsSpeaking(!isSpeaking);
    if (isSpeaking && speechSynthesis.current) {
      speechSynthesis.current.cancel();
    }
  };

  const handleGetRecommendations = () => {
    if (!isAuthenticated) {
      toast.error('Please login to get personalized recommendations');
      return;
    }
    setShowRecommendations(true);
    recommendationsMutation.mutate(userPreferences);
  };

  const clearChat = async () => {
    const sid = localStorage.getItem(SESSION_STORAGE_KEY);
    if (sid) {
      try { await apiService.deleteChatSession(sid); } catch (e) {}
    }
    const newId = generateSessionId();
    localStorage.setItem(SESSION_STORAGE_KEY, newId);
    setSessionId(newId);
    setMessages([{ type: 'assistant', content: 'Chat cleared! How can I help you with your travel plans?', timestamp: new Date() }]);
  };

  const quickActions = [
    { icon: MapPin, label: 'Find Destinations', action: () => handleSendMessage('Show me popular destinations') },
    { icon: Calendar, label: 'Plan Trip', action: () => handleSendMessage('Help me plan a trip') },
    { icon: DollarSign, label: 'Budget Help', action: () => handleSendMessage('Help me plan a budget-friendly trip') },
    { icon: Plane, label: 'Flight Tips', action: () => handleSendMessage('Give me flight booking tips') },
    { icon: Camera, label: 'Photo Spots', action: () => handleSendMessage('Best photography destinations') },
    { icon: Heart, label: 'Romantic Places', action: () => handleSendMessage('Romantic destinations for couples') }
  ];

  const aiFeatures = [
    { icon: Sparkles, title: 'Smart Recommendations', description: 'AI-powered suggestions based on your preferences', color: 'from-blue-500 to-purple-600' },
    { icon: Globe, title: 'Global Knowledge', description: 'Information about destinations worldwide', color: 'from-green-500 to-emerald-600' },
    { icon: Zap, title: 'Instant Responses', description: 'Get answers to your travel questions immediately', color: 'from-orange-500 to-red-600' },
    { icon: Users, title: 'Personalized Service', description: 'Tailored advice for your travel style', color: 'from-purple-500 to-pink-600' }
  ];

  return (
    <div className="min-h-screen pt-20">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Bot className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-gradient mb-4">AI Travel Assistant</h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">Get personalized travel recommendations and expert advice powered by advanced AI technology</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Chat Interface */}
          <div className="lg:col-span-3">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }} className="glass rounded-2xl overflow-hidden">
              {/* Chat Header */}
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">AI Travel Assistant</h3>
                    <p className="text-gray-400 text-sm">Online • Ready to help</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={toggleSpeech} className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${isSpeaking ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`} title={isSpeaking ? 'Disable speech' : 'Enable speech'}>
                    {isSpeaking ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                  </button>
                  <button onClick={clearChat} className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors" title="Clear chat">
                    <RefreshCw className="w-4 h-4 text-gray-300" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="h-96 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div key={index} initial={{ opacity: 0, x: message.type === 'user' ? 20 : -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3 }} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                        <div className={`px-4 py-3 rounded-2xl ${message.type === 'user' ? 'bg-primary-500 text-white' : message.isError ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 'bg-gray-700 text-gray-200'}`}>
                          {message.type === 'assistant' && (
                            <div className="flex items-center gap-2 mb-2">
                              <Bot className="w-4 h-4" />
                              <span className="text-xs font-medium">AI Assistant</span>
                            </div>
                          )}
                          <div className="whitespace-pre-wrap text-sm">{message.content}</div>

                          {/* Recommendations structured list support */}
                          {message.recommendationsList && (
                            <ul className="mt-3 list-disc list-inside text-sm space-y-1 text-gray-200">
                              {message.recommendationsList.map((line, i) => (
                                <li key={i}>{line}</li>
                              ))}
                            </ul>
                          )}

                          {/* Previous rich recommendations support */}
                          {message.recommendations && (
                            <div className="mt-4 space-y-3">
                              {message.recommendations.top_destinations?.map((dest, i) => (
                                <div key={i} className="bg-black/20 rounded-lg p-3">
                                  <h4 className="font-semibold text-primary-300">{dest.name}, {dest.country}</h4>
                                  <p className="text-xs text-gray-300 mb-2">{dest.reason}</p>
                                  <div className="flex items-center gap-4 text-xs text-gray-400">
                                    <span>🕒 {dest.best_time}</span>
                                    <span>💰 {dest.estimated_budget}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <div className={`text-xs text-gray-400 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center mx-2 ${message.type === 'user' ? 'order-1 bg-primary-500' : 'order-2 bg-gray-600'}`}>
                        {message.type === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {isLoading && (
                  <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex justify-start">
                    <div className="bg-gray-700 text-gray-200 max-w-xs lg:max-w-md px-4 py-3 rounded-2xl">
                      <div className="flex items-center gap-2 mb-2">
                        <Bot className="w-4 h-4" />
                        <span className="text-xs font-medium">AI Assistant</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-white/10">
                <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex gap-2">
                  <div className="flex-1 relative">
                    <input type="text" value={inputMessage} onChange={(e) => setInputMessage(e.target.value)} placeholder="Ask me anything about travel..." className="input-futuristic w-full px-4 py-3 rounded-full pr-12" disabled={isLoading} />
                    <button type="button" onClick={handleVoiceInput} className={`absolute right-12 top-1/2 transform -translate-y-1/2 w-8 h-8 rounded-full flex items-center justify-center transition-colors ${isListening ? 'bg-red-500 text-white' : 'text-gray-400 hover:text-white'}`} disabled={isLoading}>
                      {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>
                  </div>
                  <button type="submit" disabled={isLoading || !inputMessage.trim()} className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors disabled:opacity-50">
                    <Send className="w-5 h-5 text-white" />
                  </button>
                </form>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.4 }} className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Zap className="w-5 h-5" />Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, index) => (
                  <button key={index} onClick={action.action} className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors text-center">
                    <action.icon className="w-5 h-5 text-primary-400 mx-auto mb-1" />
                    <span className="text-white text-xs">{action.label}</span>
                  </button>
                ))}
              </div>
            </motion.div>

            {/* AI Features */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.6 }} className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5" />AI Features</h3>
              <div className="space-y-4">
                {aiFeatures.map((feature, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <div className={`w-10 h-10 bg-gradient-to-br ${feature.color} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <feature.icon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h4 className="text-white font-medium text-sm">{feature.title}</h4>
                      <p className="text-gray-300 text-xs">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Get Recommendations */}
            {isAuthenticated && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.8 }} className="glass rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><TrendingUp className="w-5 h-5" />Personalized Recommendations</h3>
                <p className="text-gray-300 text-sm mb-4">Get AI-powered travel recommendations based on your preferences</p>
                <button onClick={handleGetRecommendations} disabled={recommendationsMutation.isLoading} className="btn-gradient w-full py-3 rounded-lg font-semibold hover:shadow-glow transition-all disabled:opacity-50">
                  {recommendationsMutation.isLoading ? (
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Generating...
                    </div>
                  ) : (
                    'Get Recommendations'
                  )}
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAIAssistant;