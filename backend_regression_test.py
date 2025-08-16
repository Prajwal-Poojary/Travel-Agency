#!/usr/bin/env python3
"""
Backend Regression Test - FastAPI Auth and Protected Endpoints
Specific test for the review request requirements
"""

import requests
import json
import sys
import os

# Get the backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://react-debug-portal.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class RegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name, success, message="", error_details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if error_details:
            print(f"   Error: {error_details}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append({
                "test": test_name,
                "message": message,
                "error": error_details
            })
        print()

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

    def test_1_login_demo_user(self):
        """Test 1: POST /api/auth/login -> 200 with access_token for demo@example.com/password123"""
        print("🔍 Test 1: Login with demo@example.com/password123...")
        
        login_data = {
            "email": "demo@example.com",
            "password": "password123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response is None:
            self.log_result("Login Demo User", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("Login Demo User", True, f"Login successful, token received")
                    return True
                else:
                    self.log_result("Login Demo User", False, "Missing access_token in response", str(data))
                    return False
            except json.JSONDecodeError:
                self.log_result("Login Demo User", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Login Demo User", False, f"HTTP {response.status_code}", response.text)
            return False

    def test_2_profile_with_token(self):
        """Test 2: GET /api/auth/profile with Bearer token -> 200 and JSON includes username demo_user"""
        print("🔍 Test 2: Get profile with Bearer token...")
        
        if not self.auth_token:
            self.log_result("Profile with Token", False, "No auth token available", "Login test must pass first")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = self.make_request("GET", "/auth/profile", headers=headers)
        
        if response is None:
            self.log_result("Profile with Token", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "username" in data and data["username"] == "demo_user":
                    self.log_result("Profile with Token", True, f"Profile retrieved, username: {data['username']}")
                    return True
                else:
                    self.log_result("Profile with Token", False, f"Username not 'demo_user', got: {data.get('username', 'missing')}", str(data))
                    return False
            except json.JSONDecodeError:
                self.log_result("Profile with Token", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Profile with Token", False, f"HTTP {response.status_code}", response.text)
            return False

    def test_3_chat_with_token(self):
        """Test 3: POST /api/chat with Bearer token {message:"hi"} -> 200 with session_id and response"""
        print("🔍 Test 3: Chat with Bearer token...")
        
        if not self.auth_token:
            self.log_result("Chat with Token", False, "No auth token available", "Login test must pass first")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        chat_data = {"message": "hi"}
        
        response = self.make_request("POST", "/chat", chat_data, headers=headers)
        
        if response is None:
            self.log_result("Chat with Token", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "session_id" in data and "response" in data:
                    self.log_result("Chat with Token", True, f"Chat successful, session_id: {data['session_id']}")
                    return True
                else:
                    missing = []
                    if "session_id" not in data:
                        missing.append("session_id")
                    if "response" not in data:
                        missing.append("response")
                    self.log_result("Chat with Token", False, f"Missing fields: {', '.join(missing)}", str(data))
                    return False
            except json.JSONDecodeError:
                self.log_result("Chat with Token", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Chat with Token", False, f"HTTP {response.status_code}", response.text)
            return False

    def test_4_chat_without_token(self):
        """Test 4: POST /api/chat without token -> 401"""
        print("🔍 Test 4: Chat without token (should return 401)...")
        
        chat_data = {"message": "hi"}
        response = self.make_request("POST", "/chat", chat_data)
        
        if response is None:
            self.log_result("Chat without Token", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 401:
            self.log_result("Chat without Token", True, "Correctly returned 401 Unauthorized")
            return True
        else:
            self.log_result("Chat without Token", False, f"Expected 401, got HTTP {response.status_code}", response.text)
            return False

    def test_5_destinations_public(self):
        """Test 5: GET /api/destinations -> 200 array length >=1"""
        print("🔍 Test 5: Get destinations (public endpoint)...")
        
        response = self.make_request("GET", "/destinations")
        
        if response is None:
            self.log_result("Destinations Public", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) >= 1:
                    self.log_result("Destinations Public", True, f"Retrieved {len(data)} destinations")
                    return True
                else:
                    self.log_result("Destinations Public", False, f"Expected array with length >=1, got: {type(data).__name__} with length {len(data) if isinstance(data, list) else 'N/A'}", str(data)[:200])
                    return False
            except json.JSONDecodeError:
                self.log_result("Destinations Public", False, "Invalid JSON response", response.text)
                return False
        else:
            self.log_result("Destinations Public", False, f"HTTP {response.status_code}", response.text)
            return False

    def test_6_health_check(self):
        """Test 6: GET /api/health -> 200"""
        print("🔍 Test 6: Health check...")
        
        response = self.make_request("GET", "/health")
        
        if response is None:
            self.log_result("Health Check", False, "Request failed", "Connection error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.log_result("Health Check", True, f"Health check passed: {data.get('status', 'OK')}")
                return True
            except json.JSONDecodeError:
                self.log_result("Health Check", True, "Health check passed (non-JSON response)")
                return True
        else:
            self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)
            return False

    def run_regression_tests(self):
        """Run all regression tests in order"""
        print("=" * 70)
        print("🚀 BACKEND REGRESSION TEST - FastAPI Auth and Protected Endpoints")
        print("=" * 70)
        print(f"Testing backend at: {BASE_URL}")
        print(f"API base URL: {API_BASE}")
        print()

        # Run tests in specific order
        test_results = []
        test_results.append(self.test_1_login_demo_user())
        test_results.append(self.test_2_profile_with_token())
        test_results.append(self.test_3_chat_with_token())
        test_results.append(self.test_4_chat_without_token())
        test_results.append(self.test_5_destinations_public())
        test_results.append(self.test_6_health_check())

        # Print summary
        print("=" * 70)
        print("📊 REGRESSION TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Error: {error['error']}")
        
        print("\n" + "=" * 70)
        
        # Return success status
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = RegressionTester()
    success = tester.run_regression_tests()
    
    if success:
        print("🎉 All regression tests passed! Backend auth and protected endpoints working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some regression tests failed. Please check the errors above.")
        sys.exit(1)