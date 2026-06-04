#!/usr/bin/env python3
"""
Debug script to test the registration endpoint
"""
import requests
import json

# Test data
test_user = {
    "email": "testuser@example.com",
    "password": "testpassword123"
}

# Make request to local backend
url = "http://localhost:5000/api/auth/register"

print("Testing registration endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(test_user, indent=2)}")

try:
    response = requests.post(url, json=test_user)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("\n✓ Registration successful!")
    else:
        print("\n✗ Registration failed!")
        
except requests.exceptions.ConnectionError:
    print("\n✗ Could not connect to backend!")
    print("Make sure the Flask server is running on port 5000")
except Exception as e:
    print(f"\n✗ Error: {e}")