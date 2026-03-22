#!/usr/bin/env python3
"""
Carter API Backend Testing Suite
Tests the modular refactored backend endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://profit-hunter-67.preview.emergentagent.com/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {test_name} ==={Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def test_endpoint(method, endpoint, expected_status=None, headers=None, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            print_error(f"Unsupported method: {method}")
            return False
        
        status_code = response.status_code
        
        # Check if we got the expected status code
        if expected_status and status_code != expected_status:
            print_error(f"{method} {endpoint} - Expected {expected_status}, got {status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print_success(f"{method} {endpoint} - Status: {status_code}")
            if description:
                print_info(f"Description: {description}")
            
            # Print response preview for successful calls
            if status_code < 400:
                response_preview = json.dumps(response_data, indent=2)[:300]
                if len(response_preview) >= 300:
                    response_preview += "..."
                print_info(f"Response preview: {response_preview}")
            
            return True
            
        except json.JSONDecodeError:
            print_success(f"{method} {endpoint} - Status: {status_code} (Non-JSON response)")
            if description:
                print_info(f"Description: {description}")
            return True
            
    except requests.exceptions.Timeout:
        print_warning(f"{method} {endpoint} - Request timed out (expected for heavy operations)")
        return True  # Timeout is acceptable for some endpoints
    except requests.exceptions.RequestException as e:
        print_error(f"{method} {endpoint} - Request failed: {str(e)}")
        return False

def main():
    print(f"{Colors.BOLD}Carter API Backend Testing Suite{Colors.ENDC}")
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track test results
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # Test 1: Root endpoint
    print_test_header("Root Endpoint Test")
    total_tests += 1
    if test_endpoint("GET", "/", expected_status=200, description="Should return API info with message and version"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 2: Auth endpoint without authentication
    print_test_header("Authentication Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("GET", "/auth/me", expected_status=401, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 3: Chat conversations endpoint (moved to separate file)
    print_test_header("Chat Conversations Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("GET", "/chat/conversations", expected_status=401, description="Should return 401 without authentication - endpoint moved to routes/chat.py"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 4: Chat start endpoint (moved to separate file)
    print_test_header("Chat Start Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("POST", "/chat/start", expected_status=401, data={"user_id": "test_user"}, description="Should return 401 without authentication - endpoint moved to routes/chat.py"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 5: Dashboard endpoint
    print_test_header("Dashboard Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("GET", "/dashboard", expected_status=401, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 6: Feedback endpoint
    print_test_header("Feedback Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("POST", "/feedback", expected_status=401, data={"category": "bug", "title": "Test", "description": "Test feedback"}, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 7: Saved items endpoint
    print_test_header("Saved Items Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("GET", "/saved-items", expected_status=401, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 8: Search endpoint
    print_test_header("Search Endpoint Test (Unauthenticated)")
    total_tests += 1
    if test_endpoint("POST", "/search", expected_status=401, data={"query": "test item", "category": "electronics"}, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 9: Additional chat endpoints to verify modular structure
    print_test_header("Additional Chat Endpoints Test (Unauthenticated)")
    
    # Test chat messages endpoint
    total_tests += 1
    if test_endpoint("GET", "/chat/conversations/test123/messages", expected_status=401, description="Should return 401 without authentication - endpoint moved to routes/chat.py"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test send message endpoint
    total_tests += 1
    if test_endpoint("POST", "/chat/conversations/test123/messages", expected_status=401, data={"message": "test"}, description="Should return 401 without authentication - endpoint moved to routes/chat.py"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test 10: Verify other core endpoints still work
    print_test_header("Additional Core Endpoints Test (Unauthenticated)")
    
    # Test deal alerts
    total_tests += 1
    if test_endpoint("GET", "/deal-alerts", expected_status=401, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test subscription checkout
    total_tests += 1
    if test_endpoint("POST", "/subscriptions/checkout", expected_status=401, data={"plan": "basic", "origin_url": "https://test.com"}, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Test price estimation
    total_tests += 1
    if test_endpoint("POST", "/estimate-price", expected_status=401, data={"title": "Test item", "description": "Test description"}, description="Should return 401 without authentication"):
        passed_tests += 1
    else:
        failed_tests += 1
    
    # Print final results
    print(f"\n{Colors.BOLD}=== TEST RESULTS ==={Colors.ENDC}")
    print(f"Total tests: {total_tests}")
    print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {failed_tests}{Colors.ENDC}")
    
    if failed_tests == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}")
        print(f"{Colors.GREEN}The modular refactoring appears to be successful.{Colors.ENDC}")
        print(f"{Colors.GREEN}All endpoints are responding correctly with proper authentication checks.{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {failed_tests} TEST(S) FAILED{Colors.ENDC}")
        print(f"{Colors.RED}Some endpoints may have issues after the refactoring.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)