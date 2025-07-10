import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, Send, Sparkles, MessageCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: 'Hello! I\'m your AI travel assistant. I can help you find perfect destinations, plan your trips, and answer any travel-related questions. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        type: 'assistant',
        content: 'Thank you for your question! I\'m currently being enhanced with Google Gemini AI integration. Soon I\'ll be able to provide personalized travel recommendations, help you plan trips, and answer all your travel questions in real-time.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const suggestedQuestions = [
    'What are the best destinations for summer vacation?',
    'Help me plan a romantic getaway',
    'What activities are available in Tokyo?',
    'Find me luxury resorts in the Maldives'
  ];

  return (
    <div className="min-h-screen pt-20">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-8"
        >
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gradient mb-2">AI Travel Assistant</h1>
          <p className="text-gray-300">Get personalized travel recommendations powered by AI</p>
        </motion.div>

        {/* Chat Container */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="glass rounded-2xl p-6 mb-6"
        >
          {/* Messages */}
          <div className="h-96 overflow-y-auto mb-6 space-y-4">
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: message.type === 'user' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-gray-700 text-gray-200'
                  }`}
                >
                  {message.type === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <Bot className="w-4 h-4" />
                      <span className="text-xs font-medium">AI Assistant</span>
                    </div>
                  )}
                  <p className="text-sm">{message.content}</p>
                </div>
              </motion.div>
            ))}
            
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex justify-start"
              >
                <div className="bg-gray-700 text-gray-200 max-w-xs lg:max-w-md px-4 py-3 rounded-2xl">
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-4 h-4" />
                    <span className="text-xs font-medium">AI Assistant</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me anything about travel..."
                className="input-futuristic w-full px-4 py-3 rounded-full pr-12"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors disabled:opacity-50"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
          </form>
        </motion.div>

        {/* Suggested Questions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Suggested Questions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="text-left p-3 bg-gray-800/50 rounded-lg hover:bg-gray-700/50 transition-colors"
              >
                <p className="text-gray-300 text-sm">{question}</p>
              </button>
            ))}
          </div>
        </motion.div>

        {/* AI Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="glass rounded-xl p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Smart Conversations</h3>
            <p className="text-gray-300 text-sm">Natural language understanding for intuitive travel planning</p>
          </div>

          <div className="glass rounded-xl p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Personalized Recommendations</h3>
            <p className="text-gray-300 text-sm">AI-powered suggestions based on your preferences</p>
          </div>

          <div className="glass rounded-xl p-6 text-center">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">24/7 Assistance</h3>
            <p className="text-gray-300 text-sm">Round-the-clock support for all your travel needs</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AIAssistant;