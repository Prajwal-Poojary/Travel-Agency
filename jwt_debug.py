#!/usr/bin/env python3
"""
JWT Debug Test
"""

import requests
import json
import jwt
import os
from datetime import datetime, timedelta

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

def debug_jwt():
    print("🔍 JWT Debug Test")
    print(f"API Base: {API_BASE}")
    
    # Login to get token
    login_data = {
        "email": "demo@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=30)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token received: {token[:50]}...")
        
        # Try to decode the token
        try:
            # First, let's see what's in the token without verification
            unverified = jwt.decode(token, options={"verify_signature": False})
            print(f"Token payload (unverified): {unverified}")
            
            # Now try with the secret from .env
            with open('/app/backend/.env', 'r') as f:
                for line in f:
                    if line.startswith('JWT_SECRET_KEY='):
                        secret = line.split('=', 1)[1].strip()
                        print(f"JWT Secret from .env: {secret}")
                        break
            
            # Try to decode with the secret
            verified = jwt.decode(token, secret, algorithms=['HS256'])
            print(f"Token payload (verified): {verified}")
            
        except Exception as e:
            print(f"JWT decode error: {e}")
        
        # Test profile endpoint
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.get(f"{API_BASE}/auth/profile", headers=headers, timeout=30)
        print(f"Profile response status: {profile_response.status_code}")
        print(f"Profile response: {profile_response.text}")
    else:
        print(f"Login failed: {response.text}")

if __name__ == "__main__":
    debug_jwt()