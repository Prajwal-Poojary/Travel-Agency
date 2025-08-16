#!/usr/bin/env python3
"""
Backend API Tests for Advanced Travel Platform
Tests the FastAPI backend endpoints at the cluster ingress.
"""

import requests
import json
import sys
from datetime import datetime

# Base URL from the review request
BASE_URL = "https://aichat-repair.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Demo credentials
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "password123"

class BackendTester:
    def __init__(self):
        self.access_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Backend-Test-Client/1.0'
        })
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_health(self):
        """Test GET /api/health endpoint"""
        self.log("Testing Health endpoint...")
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            self.log(f"Health Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Health Response: {json.dumps(data, indent=2)}")
                
                # Check required fields
                required_fields = ['status', 'gemini', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log(f"❌ Health check missing fields: {missing_fields}")
                    return False
                    
                if data.get('status') != 'healthy':
                    self.log(f"❌ Health status is not 'healthy': {data.get('status')}")
                    return False
                    
                self.log("✅ Health check passed")
                return True
            else:
                self.log(f"❌ Health check failed with status {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}")
            return False
    
    def test_login(self):
        """Test POST /api/auth/login endpoint"""
        self.log("Testing Login endpoint...")
        try:
            login_data = {
                "email": DEMO_EMAIL,
                "password": DEMO_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login", 
                json=login_data,
                timeout=10
            )
            
            self.log(f"Login Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Login Response: {json.dumps(data, indent=2)}")
                
                # Check for access_token
                if 'access_token' not in data:
                    self.log("❌ Login response missing access_token")
                    return False
                    
                self.access_token = data['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                self.log("✅ Login successful, token acquired")
                return True
            else:
                self.log(f"❌ Login failed with status {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {str(e)}")
            return False
    
    def test_profile(self):
        """Test GET /api/auth/profile endpoint (requires Bearer token)"""
        self.log("Testing Profile endpoint...")
        
        if not self.access_token:
            self.log("❌ No access token available for profile test")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/auth/profile", timeout=10)
            self.log(f"Profile Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Profile Response: {json.dumps(data, indent=2)}")
                
                # Check for user fields
                required_fields = ['user_id', 'username', 'email']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log(f"❌ Profile missing fields: {missing_fields}")
                    return False
                    
                if data.get('email') != DEMO_EMAIL:
                    self.log(f"❌ Profile email mismatch: expected {DEMO_EMAIL}, got {data.get('email')}")
                    return False
                    
                self.log("✅ Profile check passed")
                return True
            else:
                self.log(f"❌ Profile failed with status {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Profile error: {str(e)}")
            return False
    
    def test_chat(self):
        """Test POST /api/chat endpoint (requires Bearer token)"""
        self.log("Testing Chat endpoint...")
        
        if not self.access_token:
            self.log("❌ No access token available for chat test")
            return False
            
        try:
            chat_data = {
                "message": "Plan a 3-day trip to Tokyo under $1000"
            }
            
            response = self.session.post(
                f"{API_BASE}/chat",
                json=chat_data,
                timeout=30  # Longer timeout for AI response
            )
            
            self.log(f"Chat Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Chat Response Keys: {list(data.keys())}")
                
                # Check required fields
                required_fields = ['session_id', 'response', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log(f"❌ Chat response missing fields: {missing_fields}")
                    return False
                
                response_text = data.get('response', '')
                if not response_text or len(response_text.strip()) == 0:
                    self.log("❌ Chat response is empty")
                    return False
                
                self.log(f"Chat Response Text (first 200 chars): {response_text[:200]}...")
                self.log("✅ Chat test passed")
                return True
            else:
                self.log(f"❌ Chat failed with status {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Chat error: {str(e)}")
            return False
    
    def test_recommendations(self):
        """Test POST /api/ai/recommendations endpoint (requires Bearer token)"""
        self.log("Testing AI Recommendations endpoint...")
        
        if not self.access_token:
            self.log("❌ No access token available for recommendations test")
            return False
            
        try:
            rec_data = {
                "budget": "moderate",
                "activities": ["beach"],
                "duration": "3 days"
            }
            
            response = self.session.post(
                f"{API_BASE}/ai/recommendations",
                json=rec_data,
                timeout=30  # Longer timeout for AI response
            )
            
            self.log(f"Recommendations Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Recommendations Response Keys: {list(data.keys())}")
                
                if 'recommendations' not in data:
                    self.log("❌ Recommendations response missing 'recommendations' field")
                    return False
                
                recommendations = data['recommendations']
                if not isinstance(recommendations, list):
                    self.log(f"❌ Recommendations should be a list, got {type(recommendations)}")
                    return False
                
                if len(recommendations) == 0:
                    self.log("❌ Recommendations list is empty")
                    return False
                
                self.log(f"Recommendations count: {len(recommendations)}")
                self.log(f"First few recommendations: {recommendations[:3]}")
                self.log("✅ Recommendations test passed")
                return True
            else:
                self.log(f"❌ Recommendations failed with status {response.status_code}")
                self.log(f"Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Recommendations error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        self.log("=" * 60)
        self.log("Starting Backend API Tests")
        self.log(f"Base URL: {BASE_URL}")
        self.log(f"API Base: {API_BASE}")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Health
        results['health'] = self.test_health()
        
        # Test 2: Login (required for subsequent tests)
        results['login'] = self.test_login()
        
        # Test 3: Profile (requires login)
        results['profile'] = self.test_profile()
        
        # Test 4: Chat (requires login)
        results['chat'] = self.test_chat()
        
        # Test 5: Recommendations (requires login)
        results['recommendations'] = self.test_recommendations()
        
        # Summary
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.upper()}: {status}")
            if result:
                passed += 1
        
        self.log("=" * 60)
        self.log(f"OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 All backend tests PASSED!")
            return True
        else:
            self.log(f"⚠️  {total - passed} test(s) FAILED")
            return False

def main():
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()