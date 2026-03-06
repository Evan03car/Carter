#!/usr/bin/env python3

import requests
import json
import base64
import time
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'https://profit-hunter-67.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials (created by MongoDB setup)
TEST_SESSION_TOKEN = "test_session_1772834618667"
TEST_USER_ID = "test-user-1772834618667"

# Test data
SAMPLE_SEARCH_REQUEST = {
    "query": "vintage leather jacket",
    "category": "Clothing",
    "location": "New York",
    "max_price": 100.0
}

SAMPLE_PRICE_ESTIMATE_REQUEST = {
    "title": "Nike Air Jordan 1 Retro",
    "description": "Used Nike Air Jordan 1 sneakers in good condition",
    "listing_url": "https://www.ebay.com/itm/sample-listing"
}

SAMPLE_MARKETPLACE_ITEM = {
    "title": "Vintage Leather Jacket",
    "price": 45.0,
    "estimated_resale_price": 120.0,
    "profit_margin": 35.5,
    "platform": "eBay",
    "url": "https://www.ebay.com/itm/sample",
    "image_url": "https://via.placeholder.com/300x300",
    "location": "New York, NY",
    "category": "Clothing",
    "demand_level": "high",
    "best_resell_platform": "poshmark"
}

SAMPLE_DEAL_ALERT = {
    "category": "Electronics",
    "min_profit_margin": 25.0,
    "location": "California",
    "push_token": "test_push_token_123"
}

class ProfitHunterAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TEST_SESSION_TOKEN}'
        })
        self.test_results = []
    
    def log_test(self, endpoint: str, method: str, success: bool, message: str, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint}: {message}")
        
        self.test_results.append({
            'endpoint': endpoint,
            'method': method,
            'success': success,
            'message': message,
            'response_data': response_data
        })
    
    def test_api_root(self):
        """Test GET /api/ - API root endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') and data.get('version'):
                    self.log_test("/", "GET", True, f"API root working - {data.get('message')}")
                    return True
                else:
                    self.log_test("/", "GET", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test("/", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/", "GET", False, f"Exception: {str(e)}")
            return False
    
    def test_auth_me(self):
        """Test GET /api/auth/me - Get current user info"""
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('user_id') == TEST_USER_ID and data.get('email'):
                    self.log_test("/auth/me", "GET", True, f"User authenticated: {data.get('name')}")
                    return True
                else:
                    self.log_test("/auth/me", "GET", False, f"Invalid user data: {data}")
                    return False
            else:
                self.log_test("/auth/me", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/auth/me", "GET", False, f"Exception: {str(e)}")
            return False
    
    def test_dashboard(self):
        """Test GET /api/dashboard - Get dashboard data"""
        try:
            response = self.session.get(f"{API_BASE}/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                required_keys = ['user', 'stats']
                if all(key in data for key in required_keys):
                    user_data = data['user']
                    stats_data = data['stats']
                    if user_data.get('name') and 'subscription_tier' in user_data and 'saved_items' in stats_data:
                        self.log_test("/dashboard", "GET", True, f"Dashboard loaded - {user_data.get('subscription_tier')} user")
                        return True
                    else:
                        self.log_test("/dashboard", "GET", False, f"Missing required user/stats fields: {data}")
                        return False
                else:
                    self.log_test("/dashboard", "GET", False, f"Missing required keys: {data}")
                    return False
            else:
                self.log_test("/dashboard", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/dashboard", "GET", False, f"Exception: {str(e)}")
            return False
    
    def test_marketplace_search(self):
        """Test POST /api/search - Marketplace search with SerpApi"""
        try:
            response = self.session.post(f"{API_BASE}/search", json=SAMPLE_SEARCH_REQUEST)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and 'searches_remaining' in data:
                    items = data['items']
                    remaining = data['searches_remaining']
                    self.log_test("/search", "POST", True, f"Search successful - {len(items)} items found, {remaining} searches remaining")
                    return True
                else:
                    self.log_test("/search", "POST", False, f"Invalid response format: {data}")
                    return False
            elif response.status_code == 429:
                self.log_test("/search", "POST", True, "Daily search limit reached (expected for free trial)")
                return True
            else:
                self.log_test("/search", "POST", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/search", "POST", False, f"Exception: {str(e)}")
            return False
    
    def test_price_estimation(self):
        """Test POST /api/estimate-price - AI price estimation"""
        try:
            response = self.session.post(f"{API_BASE}/estimate-price", json=SAMPLE_PRICE_ESTIMATE_REQUEST)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['estimated_price', 'confidence', 'demand_level', 'best_platform', 'analysis']
                if all(field in data for field in required_fields):
                    self.log_test("/estimate-price", "POST", True, f"Price estimation working - ${data.get('estimated_price')} ({data.get('confidence')} confidence)")
                    return True
                else:
                    self.log_test("/estimate-price", "POST", False, f"Missing required fields: {data}")
                    return False
            else:
                self.log_test("/estimate-price", "POST", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("/estimate-price", "POST", False, f"Exception: {str(e)}")
            return False
    
    def test_saved_items_crud(self):
        """Test saved items CRUD operations"""
        saved_item_id = None
        
        # Test POST /api/saved-items - Save an item
        try:
            response = self.session.post(f"{API_BASE}/saved-items", json=SAMPLE_MARKETPLACE_ITEM)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Item saved' and data.get('item_id'):
                    saved_item_id = data['item_id']
                    self.log_test("/saved-items", "POST", True, f"Item saved with ID: {saved_item_id}")
                else:
                    self.log_test("/saved-items", "POST", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("/saved-items", "POST", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("/saved-items", "POST", False, f"Exception: {str(e)}")
            return False
        
        # Test GET /api/saved-items - Get saved items
        try:
            response = self.session.get(f"{API_BASE}/saved-items")
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    self.log_test("/saved-items", "GET", True, f"Retrieved {len(data['items'])} saved items")
                else:
                    self.log_test("/saved-items", "GET", True, "No saved items found (empty list)")
            else:
                self.log_test("/saved-items", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("/saved-items", "GET", False, f"Exception: {str(e)}")
            return False
        
        # Test DELETE /api/saved-items/{item_id} - Delete saved item
        if saved_item_id:
            try:
                response = self.session.delete(f"{API_BASE}/saved-items/{saved_item_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('message') == 'Item deleted':
                        self.log_test(f"/saved-items/{saved_item_id}", "DELETE", True, "Item deleted successfully")
                        return True
                    else:
                        self.log_test(f"/saved-items/{saved_item_id}", "DELETE", False, f"Unexpected response: {data}")
                        return False
                else:
                    self.log_test(f"/saved-items/{saved_item_id}", "DELETE", False, f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test(f"/saved-items/{saved_item_id}", "DELETE", False, f"Exception: {str(e)}")
                return False
        
        return True
    
    def test_deal_alerts_crud(self):
        """Test deal alerts CRUD operations"""
        alert_id = None
        
        # Test POST /api/deal-alerts - Create deal alert
        try:
            response = self.session.post(f"{API_BASE}/deal-alerts", json=SAMPLE_DEAL_ALERT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Alert created' and data.get('alert_id'):
                    alert_id = data['alert_id']
                    self.log_test("/deal-alerts", "POST", True, f"Alert created with ID: {alert_id}")
                else:
                    self.log_test("/deal-alerts", "POST", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("/deal-alerts", "POST", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("/deal-alerts", "POST", False, f"Exception: {str(e)}")
            return False
        
        # Test GET /api/deal-alerts - Get deal alerts
        try:
            response = self.session.get(f"{API_BASE}/deal-alerts")
            
            if response.status_code == 200:
                data = response.json()
                if 'alerts' in data and len(data['alerts']) > 0:
                    self.log_test("/deal-alerts", "GET", True, f"Retrieved {len(data['alerts'])} deal alerts")
                else:
                    self.log_test("/deal-alerts", "GET", True, "No deal alerts found (empty list)")
            else:
                self.log_test("/deal-alerts", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("/deal-alerts", "GET", False, f"Exception: {str(e)}")
            return False
        
        # Test DELETE /api/deal-alerts/{alert_id} - Delete deal alert
        if alert_id:
            try:
                response = self.session.delete(f"{API_BASE}/deal-alerts/{alert_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('message') == 'Alert deleted':
                        self.log_test(f"/deal-alerts/{alert_id}", "DELETE", True, "Alert deleted successfully")
                        return True
                    else:
                        self.log_test(f"/deal-alerts/{alert_id}", "DELETE", False, f"Unexpected response: {data}")
                        return False
                else:
                    self.log_test(f"/deal-alerts/{alert_id}", "DELETE", False, f"HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                self.log_test(f"/deal-alerts/{alert_id}", "DELETE", False, f"Exception: {str(e)}")
                return False
        
        return True
    
    def test_subscription_checkout(self):
        """Test POST /api/subscriptions/checkout - Stripe checkout"""
        try:
            checkout_request = {
                "plan": "basic",
                "origin_url": BACKEND_URL
            }
            response = self.session.post(f"{API_BASE}/subscriptions/checkout", json=checkout_request)
            
            if response.status_code == 200:
                data = response.json()
                if 'url' in data and 'session_id' in data:
                    self.log_test("/subscriptions/checkout", "POST", True, f"Checkout session created: {data.get('session_id')[:20]}...")
                    return data.get('session_id')
                else:
                    self.log_test("/subscriptions/checkout", "POST", False, f"Invalid response format: {data}")
                    return None
            else:
                self.log_test("/subscriptions/checkout", "POST", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("/subscriptions/checkout", "POST", False, f"Exception: {str(e)}")
            return None
    
    def test_subscription_status(self, session_id: str):
        """Test GET /api/subscriptions/status/{session_id} - Check payment status"""
        try:
            response = self.session.get(f"{API_BASE}/subscriptions/status/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                if 'payment_status' in data:
                    status = data.get('payment_status', 'unknown')
                    self.log_test(f"/subscriptions/status/{session_id[:20]}...", "GET", True, f"Payment status: {status}")
                    return True
                else:
                    self.log_test(f"/subscriptions/status/{session_id[:20]}...", "GET", False, f"Invalid response format: {data}")
                    return False
            else:
                self.log_test(f"/subscriptions/status/{session_id[:20]}...", "GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"/subscriptions/status/{session_id[:20]}...", "GET", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("🚀 PROFIT HUNTER BACKEND API TESTS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print(f"Session Token: {TEST_SESSION_TOKEN[:20]}...")
        print("=" * 80)
        
        # High priority tests first (as per test_result.md)
        print("\n📋 HIGH PRIORITY TESTS:")
        
        # 1. API Root
        self.test_api_root()
        
        # 2. Authentication
        auth_working = self.test_auth_me()
        
        if not auth_working:
            print("\n❌ Authentication failed - skipping protected endpoint tests")
            return self.get_summary()
        
        # 3. Dashboard
        self.test_dashboard()
        
        # 4. Marketplace Search (uses SerpApi + Gemini)
        self.test_marketplace_search()
        
        # 5. AI Price Estimation (uses Gemini)
        self.test_price_estimation()
        
        print("\n📋 MEDIUM PRIORITY TESTS:")
        
        # 6. Saved Items CRUD
        self.test_saved_items_crud()
        
        # 7. Deal Alerts CRUD
        self.test_deal_alerts_crud()
        
        # 8. Stripe Subscription Checkout
        session_id = self.test_subscription_checkout()
        
        # 9. Stripe Payment Status Check
        if session_id:
            self.test_subscription_status(session_id)
        
        return self.get_summary()
    
    def get_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['method']} {result['endpoint']}: {result['message']}")
        
        print("=" * 80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = ProfitHunterAPITester()
    summary = tester.run_all_tests()