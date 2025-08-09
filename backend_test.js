#!/usr/bin/env node
/**
 * Advanced Travel Platform - Backend API Testing Suite
 * Tests all Node.js backend endpoints for functionality and data integrity
 */

const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

// Configuration
const BASE_URL = process.env.BACKEND_URL || 'http://localhost:8001';
const API_BASE = `${BASE_URL}/api`;

// Test data
const TEST_USER_DATA = {
  username: `traveler_${uuidv4().slice(0, 8)}`,
  email: `traveler_${uuidv4().slice(0, 8)}@example.com`,
  password: 'SecurePass123!',
  full_name: 'Alex Johnson'
};

class BackendTester {
  constructor() {
    this.authToken = null;
    this.userId = null;
    this.testDestinationId = null;
    this.testBookingId = null;
    this.testReviewId = null;
    this.chatSessionId = null;
    this.results = {
      passed: 0,
      failed: 0,
      errors: []
    };
  }

  logResult(testName, success, message = '', errorDetails = '') {
    const status = success ? '✅ PASS' : '❌ FAIL';
    console.log(`${status}: ${testName}`);
    if (message) console.log(`   ${message}`);
    if (errorDetails) console.log(`   Error: ${errorDetails}`);
    
    if (success) {
      this.results.passed++;
    } else {
      this.results.failed++;
      this.results.errors.push({
        test: testName,
        message,
        error: errorDetails
      });
    }
    console.log();
  }

  async makeRequest(method, endpoint, data = null, headers = {}, authRequired = false) {
    const url = `${API_BASE}${endpoint}`;
    
    if (authRequired && this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    try {
      const response = await axios({
        method,
        url,
        data,
        headers: { 'Content-Type': 'application/json', ...headers },
        timeout: 30000,
      });
      return response;
    } catch (error) {
      return error.response || null;
    }
  }

  async testHealthCheck() {
    console.log('🔍 Testing Health Check Endpoint...');
    
    try {
      const response = await this.makeRequest('GET', '/health');
      if (response && response.status === 200) {
        const data = response.data;
        if (data.status === 'healthy') {
          this.logResult('Health Check', true, `Status: ${data.status}`);
        } else {
          this.logResult('Health Check', false, 'Invalid response format', JSON.stringify(data));
        }
      } else {
        this.logResult('Health Check', false, `HTTP ${response?.status || 'No response'}`, response?.statusText || 'Connection error');
      }
    } catch (error) {
      this.logResult('Health Check', false, 'Request failed', error.message);
    }
  }

  async testUserRegistration() {
    console.log('🔍 Testing User Registration...');
    
    try {
      const response = await this.makeRequest('POST', '/auth/register', TEST_USER_DATA);
      if (response && response.status === 201) {
        const data = response.data;
        if (data.access_token && data.user_id) {
          this.authToken = data.access_token;
          this.userId = data.user_id;
          this.logResult('User Registration', true, `User created: ${data.user}`);
        } else {
          this.logResult('User Registration', false, 'Missing token or user_id', JSON.stringify(data));
        }
      } else {
        this.logResult('User Registration', false, `HTTP ${response?.status || 'No response'}`, response?.data || 'Connection error');
      }
    } catch (error) {
      this.logResult('User Registration', false, 'Request failed', error.message);
    }
  }

  async testUserLogin() {
    console.log('🔍 Testing User Login...');
    
    const loginData = {
      email: TEST_USER_DATA.email,
      password: TEST_USER_DATA.password
    };
    
    try {
      const response = await this.makeRequest('POST', '/auth/login', loginData);
      if (response && response.status === 200) {
        const data = response.data;
        if (data.access_token) {
          this.authToken = data.access_token;
          this.logResult('User Login', true, `Login successful: ${data.user}`);
        } else {
          this.logResult('User Login', false, 'Missing access token', JSON.stringify(data));
        }
      } else {
        this.logResult('User Login', false, `HTTP ${response?.status || 'No response'}`, response?.data || 'Connection error');
      }
    } catch (error) {
      this.logResult('User Login', false, 'Request failed', error.message);
    }
  }

  async testDestinations() {
    console.log('🔍 Testing Destinations Endpoints...');
    
    try {
      // Test GET all destinations
      const response = await this.makeRequest('GET', '/destinations');
      if (response && response.status === 200) {
        const data = response.data;
        if (Array.isArray(data) && data.length > 0) {
          this.testDestinationId = data[0].destination_id;
          this.logResult('Get All Destinations', true, `Retrieved ${data.length} destinations`);
        } else {
          this.logResult('Get All Destinations', false, 'No destinations found', JSON.stringify(data));
        }
      } else {
        this.logResult('Get All Destinations', false, `HTTP ${response?.status || 'No response'}`, response?.data || 'Connection error');
      }

      // Test GET featured destinations
      const featuredResponse = await this.makeRequest('GET', '/destinations/featured');
      if (featuredResponse && featuredResponse.status === 200) {
        const data = featuredResponse.data;
        if (Array.isArray(data)) {
          this.logResult('Get Featured Destinations', true, `Retrieved ${data.length} featured destinations`);
        } else {
          this.logResult('Get Featured Destinations', false, 'Invalid response format', JSON.stringify(data));
        }
      } else {
        this.logResult('Get Featured Destinations', false, `HTTP ${featuredResponse?.status || 'No response'}`, featuredResponse?.data || 'Connection error');
      }
    } catch (error) {
      this.logResult('Get Destinations', false, 'Request failed', error.message);
    }
  }

  async testAIChat() {
    console.log('🔍 Testing AI Chat Endpoints...');
    
    const chatData = {
      message: "I'm planning a trip to a tropical destination. Can you recommend some places?",
      session_id: uuidv4()
    };
    this.chatSessionId = chatData.session_id;
    
    try {
      const response = await this.makeRequest('POST', '/chat', chatData);
      if (response && response.status === 200) {
        const data = response.data;
        if (data.response && data.session_id) {
          this.logResult('AI Chat', true, `AI responded with ${data.response.length} characters`);
        } else {
          this.logResult('AI Chat', false, 'Invalid chat response', JSON.stringify(data));
        }
      } else {
        this.logResult('AI Chat', false, `HTTP ${response?.status || 'No response'}`, response?.data || 'Connection error');
      }
    } catch (error) {
      this.logResult('AI Chat', false, 'Request failed', error.message);
    }
  }

  async runAllTests() {
    console.log('=' * 60);
    console.log('🚀 ADVANCED TRAVEL PLATFORM - BACKEND API TESTING');
    console.log('=' * 60);
    console.log(`Testing backend at: ${BASE_URL}`);
    console.log(`API base URL: ${API_BASE}`);
    console.log();

    // Run tests in order
    await this.testHealthCheck();
    await this.testUserRegistration();
    await this.testUserLogin();
    await this.testDestinations();
    await this.testAIChat();

    // Print summary
    console.log('=' * 60);
    console.log('📊 TEST SUMMARY');
    console.log('=' * 60);
    console.log(`✅ Passed: ${this.results.passed}`);
    console.log(`❌ Failed: ${this.results.failed}`);
    const total = this.results.passed + this.results.failed;
    console.log(`📈 Success Rate: ${((this.results.passed / total) * 100).toFixed(1)}%`);
    
    if (this.results.errors.length > 0) {
      console.log('\n🔍 FAILED TESTS:');
      for (const error of this.results.errors) {
        console.log(`   • ${error.test}: ${error.message}`);
        if (error.error) {
          console.log(`     Error: ${error.error}`);
        }
      }
    }
    
    console.log('\n' + '=' * 60);
    
    return this.results.failed === 0;
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  const tester = new BackendTester();
  tester.runAllTests().then(success => {
    if (success) {
      console.log('🎉 All tests passed! Backend is working correctly.');
      process.exit(0);
    } else {
      console.log('⚠️  Some tests failed. Please check the errors above.');
      process.exit(1);
    }
  }).catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = BackendTester;