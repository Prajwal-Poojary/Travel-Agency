#!/usr/bin/env python3
"""
Authentication Regression Test for Advanced Travel Platform
Tests specific authentication requirements from review request
"""

import requests
import json
import os

# Get base URL from frontend .env
def get_base_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://user-login-flow-1.preview.emergentagent.com"

BASE_URL = get_base_url()
API_BASE = f"{BASE_URL}/api"

class AuthRegressionTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_session_id = None
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
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None

    def test_unauthenticated_access_blocked(self):
        """Test that unauthenticated access is blocked for protected endpoints"""
        print("🔍 Testing Unauthenticated Access Blocking...")
        
        # Test POST /api/chat (no token) -> expect 401
        response = self.make_request("POST", "/chat", {"message": "Hello"})
        if response is None:
            self.log_result("POST /api/chat (no token)", False, "Request failed", "Connection error")
        elif response.status_code == 401:
            self.log_result("POST /api/chat (no token)", True, "Correctly blocked with 401")
        else:
            self.log_result("POST /api/chat (no token)", False, f"Expected 401, got {response.status_code}", response.text)

        # Test GET /api/chat/sessions/test (no token) -> expect 401
        response = self.make_request("GET", "/chat/sessions/test")
        if response is None:
            self.log_result("GET /api/chat/sessions/test (no token)", False, "Request failed", "Connection error")
        elif response.status_code == 401:
            self.log_result("GET /api/chat/sessions/test (no token)", True, "Correctly blocked with 401")
        elif response.status_code == 404:
            self.log_result("GET /api/chat/sessions/test (no token)", False, "Endpoint not implemented", "Should return 401, not 404")
        else:
            self.log_result("GET /api/chat/sessions/test (no token)", False, f"Expected 401, got {response.status_code}", response.text)

        # Test DELETE /api/chat/sessions/test (no token) -> expect 401
        response = self.make_request("DELETE", "/chat/sessions/test")
        if response is None:
            self.log_result("DELETE /api/chat/sessions/test (no token)", False, "Request failed", "Connection error")
        elif response.status_code == 401:
            self.log_result("DELETE /api/chat/sessions/test (no token)", True, "Correctly blocked with 401")
        elif response.status_code == 404:
            self.log_result("DELETE /api/chat/sessions/test (no token)", False, "Endpoint not implemented", "Should return 401, not 404")
        else:
            self.log_result("DELETE /api/chat/sessions/test (no token)", False, f"Expected 401, got {response.status_code}", response.text)

    def test_demo_user_authentication(self):
        """Test authenticated flow with demo user"""
        print("🔍 Testing Demo User Authentication Flow...")
        
        # POST /api/auth/login with demo credentials
        login_data = {
            "email": "demo@example.com",
            "password": "password123"
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response is None:
            self.log_result("Demo User Login", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("Demo User Login", True, f"Login successful, token received")
                else:
                    self.log_result("Demo User Login", False, "Missing access_token", str(data))
                    return
            except json.JSONDecodeError:
                self.log_result("Demo User Login", False, "Invalid JSON response", response.text)
                return
        else:
            self.log_result("Demo User Login", False, f"HTTP {response.status_code}", response.text)
            return

        # GET /api/auth/profile with Bearer token -> 200, contains username demo_user
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = self.make_request("GET", "/auth/profile", headers=headers)
        if response is None:
            self.log_result("Get Profile with Token", False, "Request failed", "Connection error")
        elif response.status_code == 200:
            try:
                data = response.json()
                if "username" in data and data["username"] == "demo_user":
                    self.log_result("Get Profile with Token", True, f"Profile retrieved: {data['username']}")
                else:
                    self.log_result("Get Profile with Token", False, f"Expected username 'demo_user', got {data.get('username')}", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Profile with Token", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Profile with Token", False, f"HTTP {response.status_code}", response.text)

        # POST /api/chat with Bearer token -> 200, response string and session_id
        chat_data = {"message": "Hello"}
        response = self.make_request("POST", "/chat", chat_data, headers=headers)
        if response is None:
            self.log_result("POST /api/chat with Token", False, "Request failed", "Connection error")
        elif response.status_code == 200:
            try:
                data = response.json()
                if "response" in data and "session_id" in data:
                    self.test_session_id = data["session_id"]
                    self.log_result("POST /api/chat with Token", True, f"Chat successful, session_id: {self.test_session_id}")
                else:
                    self.log_result("POST /api/chat with Token", False, "Missing response or session_id", str(data))
            except json.JSONDecodeError:
                self.log_result("POST /api/chat with Token", False, "Invalid JSON response", response.text)
        else:
            self.log_result("POST /api/chat with Token", False, f"HTTP {response.status_code}", response.text)

        # GET /api/chat/sessions/{session_id} with token -> 200
        if self.test_session_id:
            response = self.make_request("GET", f"/chat/sessions/{self.test_session_id}", headers=headers)
            if response is None:
                self.log_result("GET Chat Session with Token", False, "Request failed", "Connection error")
            elif response.status_code == 200:
                self.log_result("GET Chat Session with Token", True, "Session retrieved successfully")
            elif response.status_code == 404:
                self.log_result("GET Chat Session with Token", False, "Endpoint not implemented", "Chat sessions endpoint missing")
            else:
                self.log_result("GET Chat Session with Token", False, f"HTTP {response.status_code}", response.text)

    def test_public_endpoints(self):
        """Test that public endpoints remain accessible"""
        print("🔍 Testing Public Endpoints...")
        
        # GET /api/destinations -> 200 array
        response = self.make_request("GET", "/destinations")
        if response is None:
            self.log_result("GET /api/destinations", False, "Request failed", "Connection error")
        elif response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/destinations", True, f"Retrieved {len(data)} destinations")
                else:
                    self.log_result("GET /api/destinations", False, "Response is not an array", str(data))
            except json.JSONDecodeError:
                self.log_result("GET /api/destinations", False, "Invalid JSON response", response.text)
        else:
            self.log_result("GET /api/destinations", False, f"HTTP {response.status_code}", response.text)

        # GET /api/destinations/countries -> 200 array
        response = self.make_request("GET", "/destinations/countries")
        if response is None:
            self.log_result("GET /api/destinations/countries", False, "Request failed", "Connection error")
        elif response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("GET /api/destinations/countries", True, f"Retrieved {len(data)} countries")
                else:
                    self.log_result("GET /api/destinations/countries", False, "Response is not an array", str(data))
            except json.JSONDecodeError:
                self.log_result("GET /api/destinations/countries", False, "Invalid JSON response", response.text)
        else:
            self.log_result("GET /api/destinations/countries", False, f"HTTP {response.status_code}", response.text)

        # GET /api/health -> 200
        response = self.make_request("GET", "/health")
        if response is None:
            self.log_result("GET /api/health", False, "Request failed", "Connection error")
        elif response.status_code == 200:
            try:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("GET /api/health", True, "Health check passed")
                else:
                    self.log_result("GET /api/health", False, "Invalid health response", str(data))
            except json.JSONDecodeError:
                self.log_result("GET /api/health", False, "Invalid JSON response", response.text)
        else:
            self.log_result("GET /api/health", False, f"HTTP {response.status_code}", response.text)

    def run_regression_tests(self):
        """Run authentication regression tests"""
        print("=" * 70)
        print("🔐 AUTHENTICATION REGRESSION TEST")
        print("=" * 70)
        print(f"Testing backend at: {BASE_URL}")
        print(f"API base URL: {API_BASE}")
        print()

        # Run tests in order
        self.test_unauthenticated_access_blocked()
        self.test_demo_user_authentication()
        self.test_public_endpoints()

        # Print summary
        print("=" * 70)
        print("📊 REGRESSION TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            print(f"📈 Success Rate: {(self.results['passed'] / total_tests * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Error: {error['error']}")
        
        print("\n" + "=" * 70)
        
        return self.results

if __name__ == "__main__":
    tester = AuthRegressionTester()
    results = tester.run_regression_tests()
    
    if results['failed'] == 0:
        print("🎉 All regression tests passed!")
    else:
        print("⚠️  Some regression tests failed. Check details above.")