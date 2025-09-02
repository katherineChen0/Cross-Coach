#!/usr/bin/env python3
"""
Simple test script for the CrossCoach API
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"

def test_api():
    """Test the main API endpoints."""
    
    print("Testing CrossCoach API...")
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"Register response: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"User created: {user_data['email']}")
        else:
            print(f"Register failed: {response.text}")
            return
    except Exception as e:
        print(f"Register error: {e}")
        return
    
    # Test 2: Login
    print("\n2. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print("Login successful, got access token")
        else:
            print(f"Login failed: {response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Set up headers for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 3: Add a log entry
    print("\n3. Testing log entry creation...")
    log_data = {
        "date": str(date.today()),
        "domain": "fitness",
        "metric": "workout_duration",
        "value": 45.0,
        "notes": "Morning workout"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/log", json=log_data, headers=headers)
        print(f"Log entry response: {response.status_code}")
        if response.status_code == 200:
            log_entry = response.json()
            print(f"Log entry created: {log_entry['metric']} = {log_entry['value']}")
        else:
            print(f"Log entry failed: {response.text}")
    except Exception as e:
        print(f"Log entry error: {e}")
    
    # Test 4: Add a journal entry
    print("\n4. Testing journal entry creation...")
    journal_data = {
        "date": str(date.today()),
        "content": "Today was a great day! I felt energized and productive.",
        "mood_score": 8.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/journal", json=journal_data, headers=headers)
        print(f"Journal entry response: {response.status_code}")
        if response.status_code == 200:
            journal_entry = response.json()
            print(f"Journal entry created with mood score: {journal_entry['value']}")
        else:
            print(f"Journal entry failed: {response.text}")
    except Exception as e:
        print(f"Journal entry error: {e}")
    
    # Test 5: Get user logs
    print("\n5. Testing get user logs...")
    try:
        response = requests.get(f"{BASE_URL}/logs", headers=headers)
        print(f"Get logs response: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            print(f"Retrieved {len(logs)} log entries")
        else:
            print(f"Get logs failed: {response.text}")
    except Exception as e:
        print(f"Get logs error: {e}")
    
    # Test 6: Get insights
    print("\n6. Testing get insights...")
    try:
        response = requests.get(f"{BASE_URL}/insights", headers=headers)
        print(f"Get insights response: {response.status_code}")
        if response.status_code == 200:
            insights = response.json()
            print(f"Retrieved {len(insights)} insights")
        else:
            print(f"Get insights failed: {response.text}")
    except Exception as e:
        print(f"Get insights error: {e}")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    test_api() 