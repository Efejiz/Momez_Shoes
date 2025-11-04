import requests
import sys
import json
from datetime import datetime
import os

class AuthenticationTester:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("BASE_URL", "https://login-tester-7.preview.emergentagent.com")
        self.api_url = f"{self.base_url}/api"
        self.admin_session_token = None
        self.admin_user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Admin credentials from test_result.md
        self.admin_email = "admin@momezshoes.com"
        self.admin_password = "Admin123!"

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def test_admin_login_success(self):
        """Test successful admin login with correct credentials"""
        print("\n🔍 Testing Admin Login - Success Case...")
        
        url = f"{self.api_url}/admin/login"
        data = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check required fields in response
                required_fields = ['id', 'email', 'name', 'session_token']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if not missing_fields:
                    self.admin_session_token = response_data['session_token']
                    self.admin_user_data = response_data
                    self.log_test("Admin Login Success", True, f"Session token received: {response_data['session_token'][:20]}...")
                    return True
                else:
                    self.log_test("Admin Login Success", False, f"Missing fields in response: {missing_fields}")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log_test("Admin Login Success", False, f"Status: {response.status_code}, Error: {error_data}")
                except:
                    self.log_test("Admin Login Success", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login Success", False, f"Exception: {str(e)}")
            return False

    def test_admin_login_failures(self):
        """Test admin login failure scenarios"""
        print("\n🔍 Testing Admin Login - Failure Cases...")
        
        # Test wrong password
        self._test_login_failure("Wrong Password", self.admin_email, "WrongPassword123!")
        
        # Test wrong email
        self._test_login_failure("Wrong Email", "wrong@email.com", self.admin_password)
        
        # Test non-admin user (if exists)
        self._test_login_failure("Non-Admin User", "user@example.com", "password123")
        
        # Test missing email
        self._test_login_failure("Missing Email", "", self.admin_password)
        
        # Test missing password
        self._test_login_failure("Missing Password", self.admin_email, "")
        
        # Test missing both fields
        self._test_login_failure("Missing Both Fields", "", "")

    def _test_login_failure(self, test_name, email, password):
        """Helper method to test login failure scenarios"""
        url = f"{self.api_url}/admin/login"
        data = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            
            # Should return 401 for authentication failures
            if response.status_code == 401:
                self.log_test(f"Admin Login Failure - {test_name}", True, "Correctly returned 401 Unauthorized")
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Admin Login Failure - {test_name}", False, f"Expected 401, got {response.status_code}: {error_data}")
                except:
                    self.log_test(f"Admin Login Failure - {test_name}", False, f"Expected 401, got {response.status_code}: {response.text[:200]}")
                    
        except Exception as e:
            self.log_test(f"Admin Login Failure - {test_name}", False, f"Exception: {str(e)}")

    def test_session_validation(self):
        """Test session validation with admin token"""
        print("\n🔍 Testing Session Validation...")
        
        if not self.admin_session_token:
            self.log_test("Session Validation", False, "No admin session token available")
            return False
        
        url = f"{self.api_url}/auth/me"
        
        # Try both cookie and header authentication
        # First try with cookie
        cookies = {'session_token': self.admin_session_token}
        
        try:
            response = requests.get(url, cookies=cookies, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Check if user has admin role
                if user_data.get('role') == 'admin':
                    self.log_test("Session Validation - Admin Role (Cookie)", True, f"User role: {user_data.get('role')}")
                    return True
                else:
                    self.log_test("Session Validation - Admin Role (Cookie)", False, f"Expected admin role, got: {user_data.get('role')}")
                    return False
            else:
                # Try with Authorization header if cookie fails
                headers = {
                    'Authorization': f'Bearer {self.admin_session_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    user_data = response.json()
                    
                    # Check if user has admin role
                    if user_data.get('role') == 'admin':
                        self.log_test("Session Validation - Admin Role (Header)", True, f"User role: {user_data.get('role')}")
                        return True
                    else:
                        self.log_test("Session Validation - Admin Role (Header)", False, f"Expected admin role, got: {user_data.get('role')}")
                        return False
                else:
                    try:
                        error_data = response.json()
                        self.log_test("Session Validation", False, f"Status: {response.status_code}, Error: {error_data}")
                    except:
                        self.log_test("Session Validation", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                    return False
                
        except Exception as e:
            self.log_test("Session Validation", False, f"Exception: {str(e)}")
            return False

    def test_session_validation_invalid_token(self):
        """Test session validation with invalid token"""
        print("\n🔍 Testing Session Validation - Invalid Token...")
        
        url = f"{self.api_url}/auth/me"
        headers = {
            'Authorization': 'Bearer invalid_token_12345',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            # Should return 401 for invalid token
            if response.status_code == 401:
                self.log_test("Session Validation - Invalid Token", True, "Correctly returned 401 for invalid token")
            else:
                self.log_test("Session Validation - Invalid Token", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Session Validation - Invalid Token", False, f"Exception: {str(e)}")

    def test_admin_protected_endpoints(self):
        """Test admin protected endpoints with admin session token"""
        print("\n🔍 Testing Admin Protected Endpoints...")
        
        if not self.admin_session_token:
            self.log_test("Admin Protected Endpoints", False, "No admin session token available")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.admin_session_token}',
            'Content-Type': 'application/json'
        }
        
        # Test admin endpoints
        endpoints = [
            ("GET", "admin/orders", "Get Admin Orders"),
            ("GET", "admin/reports/best-selling", "Get Best Selling Report"),
            ("GET", "admin/reports/regions", "Get Regions Report")
        ]
        
        for method, endpoint, test_name in endpoints:
            self._test_admin_endpoint(method, endpoint, test_name, headers)

    def _test_admin_endpoint(self, method, endpoint, test_name, headers):
        """Helper method to test admin endpoints"""
        url = f"{self.api_url}/{endpoint}"
        
        try:
            # Try with cookie first
            cookies = {'session_token': self.admin_session_token}
            
            if method == "GET":
                response = requests.get(url, cookies=cookies, headers={'Content-Type': 'application/json'})
            elif method == "POST":
                response = requests.post(url, cookies=cookies, headers={'Content-Type': 'application/json'})
            
            # If cookie fails, try with Authorization header
            if response.status_code == 401:
                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    response = requests.post(url, headers=headers)
            
            # Should return 200 for successful admin access
            if response.status_code == 200:
                self.log_test(f"Admin Endpoint - {test_name}", True, f"Successfully accessed {endpoint}")
            else:
                try:
                    error_data = response.json()
                    self.log_test(f"Admin Endpoint - {test_name}", False, f"Status: {response.status_code}, Error: {error_data}")
                except:
                    self.log_test(f"Admin Endpoint - {test_name}", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
                    
        except Exception as e:
            self.log_test(f"Admin Endpoint - {test_name}", False, f"Exception: {str(e)}")

    def test_admin_access_control(self):
        """Test that non-admin users cannot access admin endpoints"""
        print("\n🔍 Testing Admin Access Control...")
        
        # Test without any token
        self._test_access_control_no_token()
        
        # Test with invalid token
        self._test_access_control_invalid_token()

    def _test_access_control_no_token(self):
        """Test admin endpoints without any authentication token"""
        endpoints = [
            ("GET", "admin/orders", "Admin Orders - No Token"),
            ("GET", "admin/reports/best-selling", "Best Selling Report - No Token"),
            ("GET", "admin/reports/regions", "Regions Report - No Token")
        ]
        
        for method, endpoint, test_name in endpoints:
            url = f"{self.api_url}/{endpoint}"
            
            try:
                response = requests.get(url, headers={'Content-Type': 'application/json'})
                
                # Should return 401 for no authentication
                if response.status_code == 401:
                    self.log_test(f"Access Control - {test_name}", True, "Correctly denied access without token")
                else:
                    self.log_test(f"Access Control - {test_name}", False, f"Expected 401, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Access Control - {test_name}", False, f"Exception: {str(e)}")

    def _test_access_control_invalid_token(self):
        """Test admin endpoints with invalid authentication token"""
        headers = {
            'Authorization': 'Bearer invalid_token_12345',
            'Content-Type': 'application/json'
        }
        
        endpoints = [
            ("GET", "admin/orders", "Admin Orders - Invalid Token"),
            ("GET", "admin/reports/best-selling", "Best Selling Report - Invalid Token"),
            ("GET", "admin/reports/regions", "Regions Report - Invalid Token")
        ]
        
        for method, endpoint, test_name in endpoints:
            url = f"{self.api_url}/{endpoint}"
            
            try:
                response = requests.get(url, headers=headers)
                
                # Should return 401 for invalid authentication
                if response.status_code == 401:
                    self.log_test(f"Access Control - {test_name}", True, "Correctly denied access with invalid token")
                else:
                    self.log_test(f"Access Control - {test_name}", False, f"Expected 401, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Access Control - {test_name}", False, f"Exception: {str(e)}")

    def run_all_authentication_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication System Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print(f"👤 Admin credentials: {self.admin_email}")
        print("=" * 60)
        
        # Run test suites in order
        login_success = self.test_admin_login_success()
        
        # Only proceed with other tests if login was successful
        if login_success:
            self.test_session_validation()
            self.test_admin_protected_endpoints()
        
        # These tests should work regardless of login success
        self.test_admin_login_failures()
        self.test_session_validation_invalid_token()
        self.test_admin_access_control()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results if not t['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print(f"\n✅ All authentication tests passed!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = AuthenticationTester()
    success = tester.run_all_authentication_tests()
    
    # Save detailed results
    results_path = os.environ.get('RESULTS_PATH', 'auth_test_results.json')
    try:
        with open(results_path, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': tester.tests_run,
                    'passed_tests': tester.tests_passed,
                    'failed_tests': tester.tests_run - tester.tests_passed,
                    'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0,
                    'timestamp': datetime.now().isoformat(),
                    'admin_session_token': tester.admin_session_token[:20] + "..." if tester.admin_session_token else None
                },
                'detailed_results': tester.test_results
            }, f, indent=2)
    except Exception as e:
        print(f"    ⚠️ Unable to write results to {results_path}: {e}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())