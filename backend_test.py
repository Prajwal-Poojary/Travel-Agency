#!/usr/bin/env python3
"""
Advanced Travel Platform - Backend API Testing Suite
Tests all Node.js backend endpoints for functionality and data integrity
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://react-debug-portal.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test data
TEST_USER_DATA = {
    "username": f"traveler_{uuid.uuid4().hex[:8]}",
    "email": f"traveler_{uuid.uuid4().hex[:8]}@example.com",
    "password": "SecurePass123!",
    "full_name": "Alex Johnson"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_destination_id = None
        self.test_booking_id = None
        self.test_review_id = None
        self.test_tour_id = None
        self.chat_session_id = None
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

    def make_request(self, method, endpoint, data=None, headers=None, auth_required=False):
        """Make HTTP request with proper error handling"""
        url = f"{API_BASE}{endpoint}"
        
        # Add auth header if required
        if auth_required and self.auth_token:
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            return None

    def test_health_check(self):
        """Test health check endpoint"""
        print("🔍 Testing Health Check Endpoint...")
        
        response = self.make_request("GET", "/health")
        if response is None:
            self.log_result("Health Check", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health Check", True, f"Status: {data['status']}")
                else:
                    self.log_result("Health Check", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Health Check", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Health Check", False, f"HTTP {response.status_code}", response.text)

    def test_root_endpoint(self):
        """Test root endpoint"""
        print("🔍 Testing Root Endpoint...")
        
        # Test the actual root endpoint without /api prefix - should serve frontend
        try:
            response = self.session.get(BASE_URL, timeout=30)
        except:
            self.log_result("Root Endpoint", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            # Root should serve HTML for frontend
            if "<!DOCTYPE html>" in response.text and "Advanced Travel Platform" in response.text:
                self.log_result("Root Endpoint", True, "Frontend HTML served correctly")
            else:
                self.log_result("Root Endpoint", False, "Invalid HTML response", response.text[:200])
        else:
            self.log_result("Root Endpoint", False, f"HTTP {response.status_code}", response.text)

    def test_user_registration(self):
        """Test user registration"""
        print("🔍 Testing User Registration...")
        
        response = self.make_request("POST", "/auth/register", TEST_USER_DATA)
        if response is None:
            self.log_result("User Registration", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 201:
            try:
                data = response.json()
                if "access_token" in data and "user_id" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user_id"]
                    self.log_result("User Registration", True, f"User created: {data['user']}")
                else:
                    self.log_result("User Registration", False, "Missing token or user_id", str(data))
            except json.JSONDecodeError:
                self.log_result("User Registration", False, "Invalid JSON response", response.text)
        else:
            self.log_result("User Registration", False, f"HTTP {response.status_code}", response.text)

    def test_user_login(self):
        """Test user login"""
        print("🔍 Testing User Login...")
        
        login_data = {
            "email": TEST_USER_DATA["email"],
            "password": TEST_USER_DATA["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response is None:
            self.log_result("User Login", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("User Login", True, f"Login successful: {data['user']}")
                else:
                    self.log_result("User Login", False, "Missing access token", str(data))
            except json.JSONDecodeError:
                self.log_result("User Login", False, "Invalid JSON response", response.text)
        else:
            self.log_result("User Login", False, f"HTTP {response.status_code}", response.text)

    def test_user_profile(self):
        """Test user profile endpoints"""
        print("🔍 Testing User Profile...")
        
        # Test GET profile
        response = self.make_request("GET", "/auth/profile", auth_required=True)
        if response is None:
            self.log_result("Get User Profile", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "username" in data and "email" in data:
                    self.log_result("Get User Profile", True, f"Profile retrieved: {data['username']}")
                else:
                    self.log_result("Get User Profile", False, "Invalid profile data", str(data))
            except json.JSONDecodeError:
                self.log_result("Get User Profile", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get User Profile", False, f"HTTP {response.status_code}", response.text)

    def test_destinations(self):
        """Test destinations endpoints"""
        print("🔍 Testing Destinations Endpoints...")
        
        # Test GET all destinations
        response = self.make_request("GET", "/destinations")
        if response is None:
            self.log_result("Get All Destinations", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.test_destination_id = data[0].get("destination_id")
                    self.log_result("Get All Destinations", True, f"Retrieved {len(data)} destinations")
                else:
                    self.log_result("Get All Destinations", False, "No destinations found", str(data))
            except json.JSONDecodeError:
                self.log_result("Get All Destinations", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get All Destinations", False, f"HTTP {response.status_code}", response.text)

        # Test GET featured destinations
        response = self.make_request("GET", "/destinations/featured")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Featured Destinations", True, f"Retrieved {len(data)} featured destinations")
                else:
                    self.log_result("Get Featured Destinations", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Featured Destinations", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Featured Destinations", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET destination categories
        response = self.make_request("GET", "/destinations/categories")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Destination Categories", True, f"Retrieved {len(data)} categories")
                else:
                    self.log_result("Get Destination Categories", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Destination Categories", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Destination Categories", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET single destination
        if self.test_destination_id:
            response = self.make_request("GET", f"/destinations/{self.test_destination_id}")
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if "destination_id" in data and "name" in data:
                        self.log_result("Get Single Destination", True, f"Retrieved destination: {data['name']}")
                    else:
                        self.log_result("Get Single Destination", False, "Invalid destination data", str(data))
                except json.JSONDecodeError:
                    self.log_result("Get Single Destination", False, "Invalid JSON response", response.text)
            else:
                self.log_result("Get Single Destination", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

    def test_bookings(self):
        """Test bookings endpoints"""
        print("🔍 Testing Bookings Endpoints...")
        
        if not self.test_destination_id:
            self.log_result("Create Booking", False, "No destination ID available", "Skipping booking tests")
            return

        # Test CREATE booking
        booking_data = {
            "destination_id": self.test_destination_id,
            "check_in_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "check_out_date": (datetime.now() + timedelta(days=35)).isoformat(),
            "guests": 2,
            "special_requests": "Ocean view room preferred"
        }
        
        response = self.make_request("POST", "/bookings", booking_data, auth_required=True)
        if response is None:
            self.log_result("Create Booking", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 201:
            try:
                data = response.json()
                if "booking_id" in data:
                    self.test_booking_id = data["booking_id"]
                    self.log_result("Create Booking", True, f"Booking created: {data['booking_id']}")
                else:
                    self.log_result("Create Booking", False, "Missing booking_id", str(data))
            except json.JSONDecodeError:
                self.log_result("Create Booking", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Create Booking", False, f"HTTP {response.status_code}", response.text)

        # Test GET user bookings
        response = self.make_request("GET", "/bookings", auth_required=True)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get User Bookings", True, f"Retrieved {len(data)} bookings")
                else:
                    self.log_result("Get User Bookings", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get User Bookings", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get User Bookings", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET single booking
        if self.test_booking_id:
            response = self.make_request("GET", f"/bookings/{self.test_booking_id}", auth_required=True)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if "booking_id" in data:
                        self.log_result("Get Single Booking", True, f"Retrieved booking: {data['booking_id']}")
                    else:
                        self.log_result("Get Single Booking", False, "Invalid booking data", str(data))
                except json.JSONDecodeError:
                    self.log_result("Get Single Booking", False, "Invalid JSON response", response.text)
            else:
                self.log_result("Get Single Booking", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

    def test_reviews(self):
        """Test reviews endpoints"""
        print("🔍 Testing Reviews Endpoints...")
        
        if not self.test_destination_id:
            self.log_result("Create Review", False, "No destination ID available", "Skipping review tests")
            return

        # Test CREATE review
        review_data = {
            "destination_id": self.test_destination_id,
            "rating": 5,
            "comment": "Amazing destination! The scenery was breathtaking and the experience was unforgettable.",
            "verified_stay": True
        }
        
        response = self.make_request("POST", "/reviews", review_data, auth_required=True)
        if response is None:
            self.log_result("Create Review", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 201:
            try:
                data = response.json()
                if "review_id" in data:
                    self.test_review_id = data["review_id"]
                    self.log_result("Create Review", True, f"Review created: {data['review_id']}")
                else:
                    self.log_result("Create Review", False, "Missing review_id", str(data))
            except json.JSONDecodeError:
                self.log_result("Create Review", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Create Review", False, f"HTTP {response.status_code}", response.text)

        # Test GET reviews for destination
        response = self.make_request("GET", f"/reviews/{self.test_destination_id}")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Destination Reviews", True, f"Retrieved {len(data)} reviews")
                else:
                    self.log_result("Get Destination Reviews", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Destination Reviews", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Destination Reviews", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET review statistics
        response = self.make_request("GET", f"/reviews/{self.test_destination_id}/stats")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if "total_reviews" in data and "average_rating" in data:
                    self.log_result("Get Review Statistics", True, f"Stats: {data['total_reviews']} reviews, avg rating: {data['average_rating']}")
                else:
                    self.log_result("Get Review Statistics", False, "Invalid stats format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Review Statistics", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Review Statistics", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

    def test_ai_chat(self):
        """Test AI chat endpoints"""
        print("🔍 Testing AI Chat Endpoints...")
        
        # Test AI chat
        chat_data = {
            "message": "I'm planning a trip to a tropical destination. Can you recommend some places?",
            "session_id": str(uuid.uuid4())
        }
        self.chat_session_id = chat_data["session_id"]
        
        response = self.make_request("POST", "/chat", chat_data)
        if response is None:
            self.log_result("AI Chat", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "response" in data and "session_id" in data:
                    self.log_result("AI Chat", True, f"AI responded with {len(data['response'])} characters")
                else:
                    self.log_result("AI Chat", False, "Invalid chat response", str(data))
            except json.JSONDecodeError:
                self.log_result("AI Chat", False, "Invalid JSON response", response.text)
        else:
            self.log_result("AI Chat", False, f"HTTP {response.status_code}", response.text)

        # Test GET chat session
        if self.chat_session_id:
            response = self.make_request("GET", f"/chat/sessions/{self.chat_session_id}")
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if "session_id" in data and "messages" in data:
                        self.log_result("Get Chat Session", True, f"Session has {len(data['messages'])} messages")
                    else:
                        self.log_result("Get Chat Session", False, "Invalid session data", str(data))
                except json.JSONDecodeError:
                    self.log_result("Get Chat Session", False, "Invalid JSON response", response.text)
            else:
                self.log_result("Get Chat Session", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test AI recommendations (requires auth)
        if self.auth_token:
            recommendations_data = {
                "preferences": {
                    "budget": "medium",
                    "activities": ["beach", "culture"],
                    "duration": "7 days"
                }
            }
            
            response = self.make_request("POST", "/chat/recommendations", recommendations_data, auth_required=True)
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if "recommendations" in data:
                        self.log_result("AI Recommendations", True, "Recommendations generated successfully")
                    else:
                        self.log_result("AI Recommendations", False, "Invalid recommendations format", str(data))
                except json.JSONDecodeError:
                    self.log_result("AI Recommendations", False, "Invalid JSON response", response.text)
            else:
                self.log_result("AI Recommendations", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

    def test_virtual_tours(self):
        """Test virtual tours endpoints"""
        print("🔍 Testing Virtual Tours Endpoints...")
        
        # Test GET all virtual tours
        response = self.make_request("GET", "/virtual-tours")
        if response is None:
            self.log_result("Get All Virtual Tours", False, "Request failed", "Connection error")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Virtual Tours", True, f"Retrieved {len(data)} virtual tours")
                    # Store first tour ID for further testing
                    if len(data) > 0 and 'tour_id' in data[0]:
                        self.test_tour_id = data[0]['tour_id']
                else:
                    self.log_result("Get All Virtual Tours", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get All Virtual Tours", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get All Virtual Tours", False, f"HTTP {response.status_code}", response.text)

        # Test GET featured virtual tours
        response = self.make_request("GET", "/virtual-tours/featured")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Featured Virtual Tours", True, f"Retrieved {len(data)} featured tours")
                else:
                    self.log_result("Get Featured Virtual Tours", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Featured Virtual Tours", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Featured Virtual Tours", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET virtual tour types
        response = self.make_request("GET", "/virtual-tours/types")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Virtual Tour Types", True, f"Retrieved {len(data)} tour types")
                else:
                    self.log_result("Get Virtual Tour Types", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Virtual Tour Types", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Virtual Tour Types", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET virtual tour countries
        response = self.make_request("GET", "/virtual-tours/countries")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Virtual Tour Countries", True, f"Retrieved {len(data)} countries")
                else:
                    self.log_result("Get Virtual Tour Countries", False, "Invalid response format", str(data))
            except json.JSONDecodeError:
                self.log_result("Get Virtual Tour Countries", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Get Virtual Tour Countries", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test GET single virtual tour
        if hasattr(self, 'test_tour_id') and self.test_tour_id:
            response = self.make_request("GET", f"/virtual-tours/{self.test_tour_id}")
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if "tour_id" in data and "name" in data:
                        self.log_result("Get Single Virtual Tour", True, f"Retrieved tour: {data['name']}")
                    else:
                        self.log_result("Get Single Virtual Tour", False, "Invalid tour data", str(data))
                except json.JSONDecodeError:
                    self.log_result("Get Single Virtual Tour", False, "Invalid JSON response", response.text)
            else:
                self.log_result("Get Single Virtual Tour", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

        # Test virtual tour search with filters
        search_params = {
            'search': 'beach',
            'tour_type': '360_video',
            'limit': 5
        }
        response = self.make_request("GET", "/virtual-tours", data=search_params)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Virtual Tours Search", True, f"Search returned {len(data)} results")
                else:
                    self.log_result("Virtual Tours Search", False, "Invalid search response", str(data))
            except json.JSONDecodeError:
                self.log_result("Virtual Tours Search", False, "Invalid JSON response", response.text)
        else:
            self.log_result("Virtual Tours Search", False, f"HTTP {response.status_code if response else 'No response'}", response.text if response else "Connection error")

    def test_additional_endpoints(self):
        """Test additional endpoints like packages and stats"""
        print("🔍 Testing Additional Endpoints...")
        
        # Test packages endpoint
        response = self.make_request("GET", "/packages")
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_result("Get Packages", True, f"Retrieved packages data")
                except json.JSONDecodeError:
                    self.log_result("Get Packages", False, "Invalid JSON response", response.text)
            else:
                self.log_result("Get Packages", False, f"HTTP {response.status_code}", response.text)
        else:
            self.log_result("Get Packages", False, "Request failed", "Connection error")

        # Test stats endpoints
        stats_endpoints = [
            "/stats/travel-insights",
            "/stats/popular-destinations",
            "/stats/destinations-by-country"
        ]
        
        for endpoint in stats_endpoints:
            response = self.make_request("GET", endpoint)
            endpoint_name = endpoint.split('/')[-1].replace('-', ' ').title()
            if response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_result(f"Get {endpoint_name}", True, f"Retrieved {endpoint_name.lower()} data")
                    except json.JSONDecodeError:
                        self.log_result(f"Get {endpoint_name}", False, "Invalid JSON response", response.text)
                else:
                    self.log_result(f"Get {endpoint_name}", False, f"HTTP {response.status_code}", response.text)
            else:
                self.log_result(f"Get {endpoint_name}", False, "Request failed", "Connection error")

        # Test WebSocket info endpoint
        response = self.make_request("GET", "/ws")
        if response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "endpoint" in data:
                        self.log_result("WebSocket Info", True, f"WebSocket endpoint: {data['endpoint']}")
                    else:
                        self.log_result("WebSocket Info", False, "Invalid WebSocket info", str(data))
                except json.JSONDecodeError:
                    self.log_result("WebSocket Info", False, "Invalid JSON response", response.text)
            else:
                self.log_result("WebSocket Info", False, f"HTTP {response.status_code}", response.text)
        else:
            self.log_result("WebSocket Info", False, "Request failed", "Connection error")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("🚀 ADVANCED TRAVEL PLATFORM - BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing backend at: {BASE_URL}")
        print(f"API base URL: {API_BASE}")
        print()

        # Run tests in order
        self.test_root_endpoint()
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_user_profile()
        self.test_destinations()
        self.test_bookings()
        self.test_reviews()
        self.test_ai_chat()
        self.test_virtual_tours()
        self.test_additional_endpoints()

        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Error: {error['error']}")
        
        print("\n" + "=" * 60)
        
        # Return success status
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)