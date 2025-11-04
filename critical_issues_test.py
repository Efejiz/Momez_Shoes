#!/usr/bin/env python3
"""
Critical Issues Test - Focus on the main problems found during comprehensive testing
"""
import requests
import json
from datetime import datetime

class CriticalIssuesTester:
    def __init__(self, base_url="https://login-tester-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None

    def login_admin(self):
        """Login as admin to get authentication token"""
        login_data = {
            "email": "admin@momezshoes.com",
            "password": "Admin123!"
        }
        
        response = requests.post(f"{self.api_url}/admin/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.session_token = data['session_token']
            self.user_id = data['id']
            print(f"✅ Admin logged in successfully")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return False

    def test_coupon_application_fix(self):
        """Test the coupon application bug fix"""
        print("\n🎫 Testing Coupon Application Fix...")
        
        if not self.session_token:
            print("    ⚠️ No authentication token")
            return False
        
        headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
        
        # Create a coupon first
        coupon_data = {
            "code": f"TESTFIX{int(datetime.now().timestamp())}",
            "type": "percentage",
            "value": 15.0,
            "min_purchase": 100.0,
            "max_discount": 50.0,
            "expires_at": "2025-12-31T23:59:59",
            "usage_limit": 50
        }
        
        create_response = requests.post(f"{self.api_url}/admin/coupons", json=coupon_data, headers=headers)
        if create_response.status_code != 200:
            print(f"    ❌ Failed to create coupon: {create_response.status_code}")
            return False
        
        print(f"    ✅ Coupon created: {coupon_data['code']}")
        
        # Now test applying the coupon (this was failing before)
        apply_data = {
            "code": coupon_data["code"]
        }
        
        apply_response = requests.post(f"{self.api_url}/coupons/apply", json=apply_data, headers=headers)
        if apply_response.status_code == 200:
            print(f"    ✅ Coupon application works! Status: {apply_response.status_code}")
            return True
        else:
            print(f"    ❌ Coupon application still failing: {apply_response.status_code}")
            try:
                error_data = apply_response.json()
                print(f"    Error: {error_data}")
            except:
                print(f"    Error: {apply_response.text}")
            return False

    def test_order_returns_endpoint(self):
        """Test the order returns endpoint"""
        print("\n🔄 Testing Order Returns Endpoint...")
        
        if not self.session_token:
            print("    ⚠️ No authentication token")
            return False
        
        headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
        
        # Test get user returns (should work even if empty)
        returns_response = requests.get(f"{self.api_url}/orders/returns", headers=headers)
        if returns_response.status_code == 200:
            returns_data = returns_response.json()
            print(f"    ✅ Get user returns works! Found {len(returns_data)} returns")
            return True
        else:
            print(f"    ❌ Get user returns failed: {returns_response.status_code}")
            try:
                error_data = returns_response.json()
                print(f"    Error: {error_data}")
            except:
                print(f"    Error: {returns_response.text}")
            return False

    def test_authentication_bypass_issues(self):
        """Test authentication bypass issues found in testing"""
        print("\n🔐 Testing Authentication Bypass Issues...")
        
        # Test endpoints that should require authentication but don't
        issues_found = []
        
        # Test admin endpoints without auth
        admin_endpoints = [
            ("GET", "admin/orders"),
            ("GET", "admin/coupons"),
            ("GET", "admin/analytics/dashboard"),
            ("GET", "admin/reports/best-selling"),
            ("GET", "admin/reports/regions")
        ]
        
        for method, endpoint in admin_endpoints:
            response = requests.get(f"{self.api_url}/{endpoint}")
            if response.status_code == 200:
                issues_found.append(f"{method} {endpoint} - No auth required (SECURITY ISSUE)")
            else:
                print(f"    ✅ {endpoint} properly requires authentication")
        
        # Test user endpoints without auth
        user_endpoints = [
            ("GET", "auth/me"),
            ("GET", "cart"),
            ("GET", "orders"),
            ("GET", "wishlist"),
            ("GET", "profile/addresses")
        ]
        
        for method, endpoint in user_endpoints:
            response = requests.get(f"{self.api_url}/{endpoint}")
            if response.status_code == 200:
                issues_found.append(f"{method} {endpoint} - No auth required (SECURITY ISSUE)")
            else:
                print(f"    ✅ {endpoint} properly requires authentication")
        
        if issues_found:
            print(f"\n    ❌ SECURITY ISSUES FOUND:")
            for issue in issues_found:
                print(f"      - {issue}")
            return False
        else:
            print(f"    ✅ All endpoints properly require authentication")
            return True

    def run_critical_tests(self):
        """Run all critical issue tests"""
        print("🚨 CRITICAL ISSUES TESTING")
        print("=" * 50)
        
        if not self.login_admin():
            return False
        
        results = []
        
        # Test the specific issues found
        results.append(("Coupon Application Fix", self.test_coupon_application_fix()))
        results.append(("Order Returns Endpoint", self.test_order_returns_endpoint()))
        results.append(("Authentication Bypass Issues", self.test_authentication_bypass_issues()))
        
        # Print summary
        print("\n" + "=" * 50)
        print("🔍 CRITICAL ISSUES TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")
            if success:
                passed += 1
        
        print(f"\nResults: {passed}/{total} critical issues resolved")
        
        if passed == total:
            print("🎉 ALL CRITICAL ISSUES RESOLVED!")
        else:
            print("⚠️  Some critical issues still need attention")
        
        return passed == total

if __name__ == "__main__":
    tester = CriticalIssuesTester()
    success = tester.run_critical_tests()
    exit(0 if success else 1)