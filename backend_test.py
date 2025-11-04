import requests
import sys
import json
from datetime import datetime
import uuid
import os

class EcommerceAPITester:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("BASE_URL", "https://login-tester-7.preview.emergentagent.com")
        self.api_url = f"{self.base_url}/api"
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.session_token and expected_status != 401:
            test_headers['Authorization'] = f'Bearer {self.session_token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic Endpoints...")
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test products endpoint (should work without auth)
        self.run_test("Get All Products", "GET", "products", 200)
        
        # Test products by category
        categories = ["men", "women", "sports", "new_arrivals"]
        for category in categories:
            self.run_test(f"Get {category.title()} Products", "GET", f"products?category={category}", 200)
        
        # Test featured products
        self.run_test("Get Featured Products", "GET", "products?featured=true", 200)
        
        # Test shipping regions
        self.run_test("Get Shipping Regions", "GET", "shipping-regions", 200)

    def test_product_details(self):
        """Test individual product endpoints"""
        print("\n🔍 Testing Product Details...")
        
        # First get a product ID
        response = requests.get(f"{self.api_url}/products")
        if response.status_code == 200:
            products = response.json()
            if products:
                # Prefer a product without existing reviews to avoid duplicate-review error
                product_id = None
                for p in products:
                    rid = p.get('id') or p.get('product_id') or p.get('uid')
                    if not rid:
                        continue
                    rev_resp = requests.get(f"{self.api_url}/products/{rid}/reviews")
                    if rev_resp.status_code == 200:
                        try:
                            revs = rev_resp.json()
                        except Exception:
                            revs = []
                        if isinstance(revs, dict) and 'reviews' in revs:
                            revs_list = revs.get('reviews') or []
                        else:
                            revs_list = revs if isinstance(revs, list) else []
                        if len(revs_list) == 0:
                            product_id = rid
                            break
                    if product_id is None:
                        product_id = products[0].get('id') or products[0].get('product_id') or products[0].get('uid')
                self.run_test("Get Product Details", "GET", f"products/{product_id}", 200)
            else:
                self.log_test("Get Product Details", False, "No products found to test")
        else:
            self.log_test("Get Product Details", False, "Could not fetch products list")

    def test_auth_endpoints_without_token(self):
        """Test auth endpoints without authentication (should fail)"""
        print("\n🔍 Testing Auth Endpoints (Unauthorized)...")
        
        # These should return 401
        self.run_test("Get User Profile (No Auth)", "GET", "auth/me", 401)
        self.run_test("Get Cart (No Auth)", "GET", "cart", 401)
        self.run_test("Get Orders (No Auth)", "GET", "orders", 401)

    def test_cart_endpoints_without_auth(self):
        """Test cart endpoints without authentication"""
        print("\n🔍 Testing Cart Endpoints (Unauthorized)...")
        
        self.run_test("Add to Cart (No Auth)", "POST", "cart/add", 401, {
            "product_id": "test-id",
            "size": "M",
            "quantity": 1
        })

    def test_admin_endpoints_without_auth(self):
        """Test admin endpoints without authentication"""
        print("\n🔍 Testing Admin Endpoints (Unauthorized)...")
        
        self.run_test("Get Admin Orders (No Auth)", "GET", "admin/orders", 401)
        self.run_test("Create Product (No Auth)", "POST", "admin/products", 401, {
            "sku": "TEST-001",
            "name_en": "Test Product",
            "name_ar": "منتج تجريبي",
            "name_tr": "Test Ürünü",
            "description_en": "Test Description",
            "description_ar": "وصف تجريبي",
            "description_tr": "Test Açıklaması",
            "price": 99.99,
            "category": "men",
            "sizes_stock": [{"size": "M", "stock": 10}]
        })
        
        self.run_test("Get Best Selling Report (No Auth)", "GET", "admin/reports/best-selling", 401)
        self.run_test("Get Regions Report (No Auth)", "GET", "admin/reports/regions", 401)

    def test_session_data_endpoint(self):
        """Test session data endpoint with mock session ID"""
        print("\n🔍 Testing Session Data Endpoint...")
        
        # This will likely fail since we don't have a real session ID from Emergent Auth
        mock_session_id = f"mock_session_{int(datetime.now().timestamp())}"
        
        response = requests.get(
            f"{self.api_url}/auth/session-data",
            headers={"X-Session-ID": mock_session_id}
        )
        
        # This should fail with 400 or similar since it's a mock session
        success = response.status_code in [400, 401, 403]  # Expected to fail
        details = f"Status: {response.status_code} (Expected failure with mock session)"
        self.log_test("Session Data with Mock ID", success, details)

    def test_invalid_endpoints(self):
        """Test invalid endpoints"""
        print("\n🔍 Testing Invalid Endpoints...")
        
        self.run_test("Invalid Product ID", "GET", "products/invalid-id", 404)
        self.run_test("Invalid Endpoint", "GET", "invalid/endpoint", 404)

    def test_data_validation(self):
        """Test data validation on endpoints"""
        print("\n🔍 Testing Data Validation...")
        
        # Test invalid cart data (without auth, should get 401 first)
        self.run_test("Invalid Cart Data", "POST", "cart/add", 401, {
            "invalid_field": "test"
        })

    def test_admin_login(self):
        """Test admin login functionality"""
        print("\n🔐 Testing Admin Login...")
        
        # Test successful admin login
        login_data = {
            "email": "admin@momezshoes.com",
            "password": "Admin123!"
        }
        
        response = self.run_test("Admin Login Success", "POST", "admin/login", 200, login_data)
        if response and 'session_token' in response:
            self.session_token = response['session_token']
            self.user_id = response['id']
            print(f"    ✅ Admin logged in successfully. Token: {self.session_token[:20]}...")
        else:
            print("    ❌ Failed to get session token from admin login")
        
        # Test failed login with wrong password
        wrong_login_data = {
            "email": "admin@momezshoes.com", 
            "password": "WrongPassword"
        }
        self.run_test("Admin Login Wrong Password", "POST", "admin/login", 401, wrong_login_data)
        
        # Test failed login with wrong email
        wrong_email_data = {
            "email": "wrong@email.com",
            "password": "Admin123!"
        }
        self.run_test("Admin Login Wrong Email", "POST", "admin/login", 401, wrong_email_data)

    def test_user_profile_addresses(self):
        """Test User Profile & Address Management"""
        print("\n🏠 Testing User Profile & Address Management...")
        
        if not self.session_token:
            print("    ⚠️ Skipping address tests - no authentication token")
            return
        
        # Test get addresses (empty initially)
        self.run_test("Get User Addresses", "GET", "profile/addresses", 200)
        
        # Test add new address
        address_data = {
            "full_name": "John Doe",
            "phone": "+90 555 123 4567",
            "address_line1": "Atatürk Caddesi No: 123",
            "address_line2": "Daire 5",
            "city": "Istanbul",
            "state": "Istanbul",
            "postal_code": "34000",
            "country": "TR",
            "is_default": True
        }
        
        response = self.run_test("Add New Address", "POST", "profile/addresses", 200, address_data)
        address_id = None
        if response and 'id' in response:
            address_id = response['id']
            print(f"    ✅ Address created with ID: {address_id}")
        
        # Test add second address (non-default)
        address_data2 = {
            "full_name": "Jane Smith",
            "phone": "+90 555 987 6543",
            "address_line1": "Bağdat Caddesi No: 456",
            "city": "Istanbul",
            "state": "Istanbul", 
            "postal_code": "34710",
            "country": "TR",
            "is_default": False
        }
        
        response2 = self.run_test("Add Second Address", "POST", "profile/addresses", 200, address_data2)
        address_id2 = None
        if response2 and 'id' in response2:
            address_id2 = response2['id']
        
        # Test get addresses again (should have 2 now)
        self.run_test("Get User Addresses After Adding", "GET", "profile/addresses", 200)
        
        # Test update address
        if address_id:
            update_data = {
                "full_name": "John Doe Updated",
                "phone": "+90 555 111 2222",
                "address_line1": "Updated Address Line 1",
                "address_line2": "Updated Apt 10",
                "city": "Ankara",
                "state": "Ankara",
                "postal_code": "06000",
                "country": "TR",
                "is_default": True
            }
            self.run_test("Update Address", "PUT", f"profile/addresses/{address_id}", 200, update_data)
        
        # Test delete address
        if address_id2:
            self.run_test("Delete Address", "DELETE", f"profile/addresses/{address_id2}", 200)
        
        # Test invalid address operations
        self.run_test("Get Invalid Address", "GET", "profile/addresses/invalid-id", 404)
        self.run_test("Update Invalid Address", "PUT", "profile/addresses/invalid-id", 404, address_data)
        self.run_test("Delete Invalid Address", "DELETE", "profile/addresses/invalid-id", 404)

    def test_password_management(self):
        """Test Password Management"""
        print("\n🔑 Testing Password Management...")
        
        if not self.session_token:
            print("    ⚠️ Skipping password tests - no authentication token")
            return
        
        # Test change password with correct old password
        change_password_data = {
            "old_password": "Admin123!",
            "new_password": "NewAdmin123!"
        }
        self.run_test("Change Password Success", "POST", "auth/change-password", 200, change_password_data)
        
        # Test change password with wrong old password
        wrong_old_password_data = {
            "old_password": "WrongOldPassword",
            "new_password": "NewAdmin123!"
        }
        self.run_test("Change Password Wrong Old", "POST", "auth/change-password", 401, wrong_old_password_data)
        
        # Change password back to original for other tests
        change_back_data = {
            "old_password": "NewAdmin123!",
            "new_password": "Admin123!"
        }
        self.run_test("Change Password Back", "POST", "auth/change-password", 200, change_back_data)
        
        # Test password reset request
        reset_request_data = {
            "email": "admin@momezshoes.com"
        }
        self.run_test("Request Password Reset", "POST", "auth/reset-password", 200, reset_request_data)
        
        # Test password reset with invalid email (should still return 200 for security)
        reset_invalid_data = {
            "email": "nonexistent@email.com"
        }
        self.run_test("Request Reset Invalid Email", "POST", "auth/reset-password", 200, reset_invalid_data)
        
        # Test confirm password reset with invalid token
        confirm_reset_data = {
            "token": "invalid-token-12345",
            "new_password": "NewPassword123!"
        }
        self.run_test("Confirm Reset Invalid Token", "POST", "auth/confirm-reset-password", 400, confirm_reset_data)

    def test_product_search_filtering(self):
        """Test Product Search & Filtering"""
        print("\n🔍 Testing Product Search & Filtering...")
        
        # Test basic search
        search_data = {
            "query": "shoe",
            "page": 1,
            "limit": 10
        }
        self.run_test("Search Products by Query", "POST", "products/search", 200, search_data)
        
        # Test search by category
        category_search_data = {
            "category": "men",
            "page": 1,
            "limit": 10
        }
        self.run_test("Search Products by Category", "POST", "products/search", 200, category_search_data)
        
        # Test search with price range
        price_search_data = {
            "min_price": 50.0,
            "max_price": 200.0,
            "page": 1,
            "limit": 10
        }
        self.run_test("Search Products by Price Range", "POST", "products/search", 200, price_search_data)
        
        # Test search with sorting
        sort_tests = [
            {"sort_by": "price_asc", "page": 1, "limit": 10},
            {"sort_by": "price_desc", "page": 1, "limit": 10},
            {"sort_by": "name", "page": 1, "limit": 10},
            {"sort_by": "created_at", "page": 1, "limit": 10}
        ]
        
        for i, sort_data in enumerate(sort_tests):
            self.run_test(f"Search Products Sort {sort_data['sort_by']}", "POST", "products/search", 200, sort_data)
        
        # Test pagination
        pagination_data = {
            "page": 2,
            "limit": 5
        }
        self.run_test("Search Products Pagination", "POST", "products/search", 200, pagination_data)
        
        # Test combined filters
        combined_search_data = {
            "query": "shoe",
            "category": "men",
            "min_price": 30.0,
            "max_price": 300.0,
            "sort_by": "price_asc",
            "page": 1,
            "limit": 20
        }
        self.run_test("Search Products Combined Filters", "POST", "products/search", 200, combined_search_data)

    def test_stripe_payment_integration(self):
        """Test Stripe Payment Integration"""
        print("\n💳 Testing Stripe Payment Integration...")
        
        if not self.session_token:
            print("    ⚠️ Skipping payment tests - no authentication token")
            return
        
        # First, we need to create an order to test payment
        # Let's try to get products first
        products_response = requests.get(f"{self.api_url}/products")
        if products_response.status_code != 200:
            print("    ⚠️ Cannot get products for payment test")
            return
        
        products = products_response.json()
        if not products:
            print("    ⚠️ No products available for payment test")
            return
        
        # Add item to cart first
        cart_data = {
            "product_id": products[0]['id'],
            "size": "M" if any(s['size'] == 'M' for s in products[0].get('sizes_stock', [])) else products[0]['sizes_stock'][0]['size'] if products[0].get('sizes_stock') else "M",
            "quantity": 1
        }
        
        add_to_cart_response = requests.post(
            f"{self.api_url}/cart/add",
            json=cart_data,
            headers={'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
        )
        
        if add_to_cart_response.status_code != 200:
            print(f"    ⚠️ Failed to add to cart: {add_to_cart_response.status_code}")
            return
        
        # Get shipping regions
        regions_response = requests.get(f"{self.api_url}/shipping-regions")
        if regions_response.status_code != 200:
            print("    ⚠️ Cannot get shipping regions for payment test")
            return
        
        regions = regions_response.json()
        if not regions:
            print("    ⚠️ No shipping regions available for payment test")
            return
        
        # Create order
        order_data = {
            "shipping_region_id": regions[0]['id'],
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "customer_phone": "+90 555 123 4567",
            "shipping_address": "Test Address, Istanbul, Turkey"
        }
        
        order_response = requests.post(
            f"{self.api_url}/orders",
            json=order_data,
            headers={'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
        )
        
        if order_response.status_code != 200:
            print(f"    ⚠️ Failed to create order: {order_response.status_code}")
            return
        
        order = order_response.json()
        order_id = order['id']
        print(f"    ✅ Created test order: {order_id}")
        
        # Test create checkout session
        checkout_data = {
            "order_id": order_id,
            "origin_url": "https://test.example.com"
        }
        
        # Note: This might fail due to Stripe integration dependencies
        response = self.run_test("Create Checkout Session", "POST", "checkout/create-session", 200, checkout_data)
        session_id = None
        if response and 'session_id' in response:
            session_id = response['session_id']
            print(f"    ✅ Checkout session created: {session_id}")
        
        # Test get checkout status
        if session_id:
            self.run_test("Get Checkout Status", "GET", f"checkout/status/{session_id}", 200)
        else:
            # Test with mock session ID
            mock_session_id = f"cs_test_{uuid.uuid4().hex[:24]}"
            self.run_test("Get Checkout Status Mock", "GET", f"checkout/status/{mock_session_id}", 404)
        
        # Test webhook endpoint (should accept POST)
        webhook_data = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "checkout.session.completed"
        }
        
        # Note: This will likely fail without proper Stripe signature
        webhook_response = requests.post(
            f"{self.api_url}/webhook/stripe",
            json=webhook_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Webhook should return some response (200 or error)
        success = webhook_response.status_code in [200, 400, 401, 403]
        details = f"Status: {webhook_response.status_code} (Webhook endpoint accessible)"
        self.log_test("Stripe Webhook Endpoint", success, details)

    def test_email_password_registration_login(self):
        """Test Email/Password Registration & Login"""
        print("\n📧 Testing Email/Password Registration & Login...")
        
        # Test user registration
        register_data = {
            "email": f"testuser_{int(datetime.now().timestamp())}@example.com",
            "password": "TestPassword123!",
            "name": "Test User"
        }
        
        response = self.run_test("User Registration", "POST", "auth/register", 200, register_data)
        user_token = None
        if response and 'session_token' in response:
            user_token = response['session_token']
            print(f"    ✅ User registered successfully. Token: {user_token[:20]}...")
        
        # Test duplicate registration (should fail)
        self.run_test("Duplicate Registration", "POST", "auth/register", 400, register_data)
        
        # Test user login with correct credentials
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        response = self.run_test("User Login Success", "POST", "auth/login", 200, login_data)
        
        # Test login with wrong password
        wrong_login_data = {
            "email": register_data["email"],
            "password": "WrongPassword"
        }
        self.run_test("User Login Wrong Password", "POST", "auth/login", 401, wrong_login_data)
        
        # Test login with non-existent email
        nonexistent_login_data = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!"
        }
        self.run_test("User Login Non-existent Email", "POST", "auth/login", 401, nonexistent_login_data)

    def test_product_reviews_ratings(self):
        """Test Product Reviews & Ratings"""
        print("\n⭐ Testing Product Reviews & Ratings...")
        
        if not self.session_token:
            print("    ⚠️ Skipping review tests - no authentication token")
            return
        
        # Get a product to review
        products_response = requests.get(f"{self.api_url}/products")
        if products_response.status_code != 200:
            print("    ⚠️ Cannot get products for review test")
            return
        
        products = products_response.json()
        if not products:
            print("    ⚠️ No products available for review test")
            return
        
        # Get current user id to avoid reviewing a product twice
        me_resp = requests.get(f"{self.api_url}/auth/me", headers={'Authorization': f'Bearer {self.session_token}'})
        user_id = None
        if me_resp.status_code == 200:
            try:
                me = me_resp.json()
                user_id = me.get('id')
            except Exception:
                user_id = None
        
        # Prefer a product not yet reviewed by this user
        product_id = None
        if user_id:
            for p in products:
                rid = p.get('id') or p.get('product_id') or p.get('uid')
                if not rid:
                    continue
                rev_resp = requests.get(f"{self.api_url}/products/{rid}/reviews")
                if rev_resp.status_code == 200:
                    try:
                        revs = rev_resp.json()
                    except Exception:
                        revs = []
                    # Normalize reviews list
                    if isinstance(revs, dict) and 'reviews' in revs:
                        revs_list = revs.get('reviews') or []
                    else:
                        revs_list = revs if isinstance(revs, list) else []
                    if not any(r.get('user_id') == user_id for r in revs_list):
                        product_id = rid
                        break
        
        if product_id is None:
            # Fallback: choose first available product id
            product_id = products[0].get('id') or products[0].get('product_id') or products[0].get('uid')
        
        # Test add review
        review_data = {
            "product_id": product_id,
            "rating": 5,
            "comment": "Excellent shoes! Very comfortable and stylish."
        }
        self.run_test("Add Product Review", "POST", "products/reviews", 200, review_data)
        
        # Test add duplicate review (should fail)
        self.run_test("Add Duplicate Review", "POST", "products/reviews", 400, review_data)
        
        # Test invalid rating
        invalid_review_data = {
            "product_id": product_id,
            "rating": 6,  # Invalid rating > 5
            "comment": "Invalid rating test"
        }
        self.run_test("Add Review Invalid Rating", "POST", "products/reviews", 400, invalid_review_data)
        
        # Test get product reviews
        self.run_test("Get Product Reviews", "GET", f"products/{product_id}/reviews", 200)
        
        # Test get product rating
        self.run_test("Get Product Rating", "GET", f"products/{product_id}/rating", 200)

    def test_wishlist(self):
        """Test Wishlist Functionality"""
        print("\n💝 Testing Wishlist...")
        
        if not self.session_token:
            print("    ⚠️ Skipping wishlist tests - no authentication token")
            return
        
        # Get a product for wishlist
        products_response = requests.get(f"{self.api_url}/products")
        if products_response.status_code != 200:
            print("    ⚠️ Cannot get products for wishlist test")
            return
        
        products = products_response.json()
        if not products:
            print("    ⚠️ No products available for wishlist test")
            return
        
        product_id = products[0]['id']
        
        # Test get empty wishlist
        self.run_test("Get Empty Wishlist", "GET", "wishlist", 200)
        
        # Test add to wishlist
        self.run_test("Add to Wishlist", "POST", f"wishlist/add/{product_id}", 200)
        
        # Test add duplicate to wishlist (should fail)
        self.run_test("Add Duplicate to Wishlist", "POST", f"wishlist/add/{product_id}", 400)
        
        # Test get wishlist with items
        self.run_test("Get Wishlist with Items", "GET", "wishlist", 200)
        
        # Test remove from wishlist
        self.run_test("Remove from Wishlist", "DELETE", f"wishlist/remove/{product_id}", 200)
        
        # Test remove non-existent item from wishlist
        self.run_test("Remove Non-existent from Wishlist", "DELETE", f"wishlist/remove/{product_id}", 404)

    def test_coupon_system(self):
        """Test Coupon System"""
        print("\n🎫 Testing Coupon System...")
        
        if not self.session_token:
            print("    ⚠️ Skipping coupon tests - no authentication token")
            return
        
        # Test create coupon (admin only)
        coupon_data = {
            "code": f"TEST{int(datetime.now().timestamp())}",
            "type": "percentage",
            "value": 10.0,
            "min_purchase": 50.0,
            "max_discount": 20.0,
            "expires_at": "2025-12-31T23:59:59",
            "usage_limit": 100
        }
        
        response = self.run_test("Create Coupon", "POST", "admin/coupons", 200, coupon_data)
        coupon_code = coupon_data["code"]
        
        # Test get all coupons (admin only)
        self.run_test("Get All Coupons", "GET", "admin/coupons", 200)
        
        # Test apply valid coupon
        apply_coupon_data = {
            "code": coupon_code
        }
        self.run_test("Apply Valid Coupon", "POST", "coupons/apply", 200, apply_coupon_data)
        
        # Test apply invalid coupon
        invalid_coupon_data = {
            "code": "INVALIDCOUPON"
        }
        self.run_test("Apply Invalid Coupon", "POST", "coupons/apply", 404, invalid_coupon_data)
        
        # Test create duplicate coupon (should fail)
        self.run_test("Create Duplicate Coupon", "POST", "admin/coupons", 400, coupon_data)

    def test_shipping_tracking(self):
        """Test Shipping Tracking"""
        print("\n📦 Testing Shipping Tracking...")
        
        if not self.session_token:
            print("    ⚠️ Skipping shipping tracking tests - no authentication token")
            return
        
        # First create an order to track
        order_id = self.create_test_order()
        if not order_id:
            print("    ⚠️ Cannot create order for tracking test")
            return
        
        # Test update tracking (admin only)
        tracking_data = {
            "tracking_number": f"TRK{int(datetime.now().timestamp())}",
            "carrier": "DHL Express",
            "status": "shipped",
            "estimated_delivery": "2024-12-31T18:00:00"
        }
        
        self.run_test("Update Shipping Tracking", "POST", f"admin/orders/{order_id}/tracking", 200, tracking_data)
        
        # Test get tracking info
        self.run_test("Get Tracking Info", "GET", f"orders/{order_id}/tracking", 200)
        
        # Test get tracking for non-existent order
        self.run_test("Get Tracking Non-existent Order", "GET", "orders/invalid-order-id/tracking", 404)

    def test_order_return_refund(self):
        """Test Order Return/Refund System"""
        print("\n🔄 Testing Order Return/Refund...")
        
        if not self.session_token:
            print("    ⚠️ Skipping return/refund tests - no authentication token")
            return
        
        # Create an order to return
        order_id = self.create_test_order()
        if not order_id:
            print("    ⚠️ Cannot create order for return test")
            return
        
        # Test request return
        return_data = {
            "order_id": order_id,
            "reason": "Product defective - sole separated from upper"
        }
        
        response = self.run_test("Request Order Return", "POST", "orders/return", 200, return_data)
        return_id = None
        if response and 'return_id' in response:
            return_id = response['return_id']
        
        # Test duplicate return request (should fail)
        self.run_test("Request Duplicate Return", "POST", "orders/return", 400, return_data)
        
        # Test get user returns
        self.run_test("Get User Returns", "GET", "orders/returns", 200)
        
        # Test get all returns (admin only)
        self.run_test("Get All Returns Admin", "GET", "admin/returns", 200)
        
        # Test update return status (admin only)
        if return_id:
            self.run_test("Update Return Status", "PATCH", f"admin/returns/{return_id}/status?status=approved", 200)
        
        # Test return for non-existent order
        invalid_return_data = {
            "order_id": "invalid-order-id",
            "reason": "Test reason"
        }
        self.run_test("Return Non-existent Order", "POST", "orders/return", 404, invalid_return_data)

    def test_contact_form(self):
        """Test Contact Form"""
        print("\n📞 Testing Contact Form...")
        
        # Test submit contact form (no auth required)
        contact_data = {
            "name": "John Customer",
            "email": "customer@example.com",
            "subject": "Question about shoe sizes",
            "message": "Hi, I need help choosing the right size for my feet. Can you provide a size guide?"
        }
        
        self.run_test("Submit Contact Form", "POST", "contact", 200, contact_data)
        
        # Test get contact messages (admin only)
        if self.session_token:
            self.run_test("Get Contact Messages Admin", "GET", "admin/contacts", 200)
            
            # Test update contact status (admin only) - we'll use a mock ID since we don't know the real ID
            mock_message_id = str(uuid.uuid4())
            self.run_test("Update Contact Status", "PATCH", f"admin/contacts/{mock_message_id}/status?status=read", 404)
        
        # Test submit contact form with missing fields
        invalid_contact_data = {
            "name": "John",
            # Missing required fields
        }
        self.run_test("Submit Invalid Contact Form", "POST", "contact", 422, invalid_contact_data)

    def test_admin_analytics_dashboard(self):
        """Test Admin Analytics Dashboard"""
        print("\n📊 Testing Admin Analytics Dashboard...")
        
        if not self.session_token:
            print("    ⚠️ Skipping analytics tests - no authentication token")
            return
        
        # Test get dashboard analytics (admin only)
        self.run_test("Get Dashboard Analytics", "GET", "admin/analytics/dashboard", 200)
        
        # Test existing admin reports
        self.run_test("Get Best Selling Products", "GET", "admin/reports/best-selling", 200)
        self.run_test("Get Active Regions Report", "GET", "admin/reports/regions", 200)

    def create_test_order(self):
        """Helper method to create a test order"""
        try:
            # Get products
            products_response = requests.get(f"{self.api_url}/products")
            if products_response.status_code != 200:
                return None
            
            products = products_response.json()
            if not products:
                return None
            
            # Add to cart
            cart_data = {
                "product_id": products[0]['id'],
                "size": "M" if any(s['size'] == 'M' for s in products[0].get('sizes_stock', [])) else products[0]['sizes_stock'][0]['size'] if products[0].get('sizes_stock') else "M",
                "quantity": 1
            }
            
            cart_response = requests.post(
                f"{self.api_url}/cart/add",
                json=cart_data,
                headers={'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            )
            
            if cart_response.status_code != 200:
                return None
            
            # Get shipping regions
            regions_response = requests.get(f"{self.api_url}/shipping-regions")
            if regions_response.status_code != 200:
                return None
            
            regions = regions_response.json()
            if not regions:
                return None
            
            # Create order
            order_data = {
                "shipping_region_id": regions[0]['id'],
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "customer_phone": "+90 555 123 4567",
                "shipping_address": "Test Address, Istanbul, Turkey"
            }
            
            order_response = requests.post(
                f"{self.api_url}/orders",
                json=order_data,
                headers={'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            )
            
            if order_response.status_code == 200:
                order = order_response.json()
                return order['id']
            
            return None
        except Exception as e:
            print(f"    ⚠️ Error creating test order: {str(e)}")
            return None

    def test_backend_api_health(self):
        """Test Backend API Health"""
        print("\n🏥 Testing Backend API Health...")
        
        # Test all new endpoints accessibility
        endpoints_to_test = [
            ("GET", "profile/addresses", 401),  # Should require auth
            ("POST", "profile/addresses", 401),  # Should require auth
            ("POST", "auth/change-password", 401),  # Should require auth
            ("POST", "auth/reset-password", 422),  # Should work without auth
            ("POST", "auth/confirm-reset-password", 422),  # Should fail with invalid data
            ("POST", "products/search", 200),  # Should work without auth
            ("POST", "checkout/create-session", 401),  # Should require auth
            ("POST", "webhook/stripe", 200),  # Should be accessible (might return error but endpoint exists)
            ("POST", "auth/register", 422),  # Should fail with missing data
            ("POST", "auth/login", 422),  # Should fail with missing data
            ("GET", "wishlist", 401),  # Should require auth
            ("POST", "coupons/apply", 401),  # Should require auth
            ("GET", "admin/coupons", 401),  # Should require admin auth
            ("POST", "contact", 422),  # Should fail with missing data
            ("GET", "admin/analytics/dashboard", 401),  # Should require admin auth
        ]
        
        for method, endpoint, expected_status in endpoints_to_test:
            test_data = {} if method == "POST" else None
            self.run_test(f"Health Check {method} {endpoint}", method, endpoint, expected_status, test_data)
        
        # Test authentication requirements
        if self.session_token:
            # Test authenticated endpoints
            auth_endpoints = [
                ("GET", "profile/addresses", 200),
                ("GET", "auth/me", 200),
                ("GET", "cart", 200),
                ("GET", "orders", 200),
                ("GET", "wishlist", 200),
                ("GET", "orders/returns", 200),
                ("GET", "admin/coupons", 200),
                ("GET", "admin/contacts", 200),
                ("GET", "admin/analytics/dashboard", 200),
                ("GET", "admin/returns", 200)
            ]
            
            for method, endpoint, expected_status in auth_endpoints:
                self.run_test(f"Auth Required {method} {endpoint}", method, endpoint, expected_status)
        
        # Test error handling
        error_test_data = [
            ("GET", "profile/addresses/nonexistent", 404),
            ("PUT", "profile/addresses/nonexistent", 404),
            ("DELETE", "profile/addresses/nonexistent", 404),
            ("GET", "checkout/status/nonexistent", 404),
            ("GET", "products/nonexistent/reviews", 200),  # Should return empty array
            ("GET", "products/nonexistent/rating", 200),  # Should return 0 rating
            ("DELETE", "wishlist/remove/nonexistent", 404),
            ("GET", "orders/nonexistent/tracking", 404)
        ]
        
        for method, endpoint, expected_status in error_test_data:
            test_data = {"test": "data"} if method in ["PUT", "POST"] else None
            self.run_test(f"Error Handling {method} {endpoint}", method, endpoint, expected_status, test_data)

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Momez Shoes E-commerce Backend API Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print("🎯 COMPREHENSIVE TEST OF ALL 15+ NEW FEATURES")
        print("=" * 80)
        
        # First login as admin to get authentication token
        self.test_admin_login()
        
        # ===== TEST ALL 15+ NEW FEATURES =====
        print("\n🎯 TESTING ALL NEW FEATURES:")
        
        # 1. Email/Password Registration & Login
        self.test_email_password_registration_login()
        
        # 2. Product Reviews & Ratings
        self.test_product_reviews_ratings()
        
        # 3. Wishlist
        self.test_wishlist()
        
        # 4. Coupon System
        self.test_coupon_system()
        
        # 5. Shipping Tracking
        self.test_shipping_tracking()
        
        # 6. Order Return/Refund
        self.test_order_return_refund()
        
        # 7. Contact Form
        self.test_contact_form()
        
        # 8. Admin Analytics Dashboard
        self.test_admin_analytics_dashboard()
        
        # 9. Previously Added Features (Quick check)
        print("\n🔄 TESTING PREVIOUSLY ADDED FEATURES:")
        self.test_user_profile_addresses()
        self.test_password_management()
        self.test_product_search_filtering()
        self.test_stripe_payment_integration()
        
        # Backend API Health Check
        self.test_backend_api_health()
        
        # Run basic tests
        print("\n🔧 TESTING BASIC FUNCTIONALITY:")
        self.test_basic_endpoints()
        self.test_product_details()
        self.test_auth_endpoints_without_token()
        self.test_cart_endpoints_without_auth()
        self.test_admin_endpoints_without_auth()
        self.test_session_data_endpoint()
        self.test_invalid_endpoints()
        self.test_data_validation()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY - ALL 15+ FEATURES")
        print("=" * 80)
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
            print(f"\n🎉 ALL TESTS PASSED! All 15+ features are working correctly!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = EcommerceAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results_path = os.environ.get('RESULTS_PATH', 'backend_test_results.json')
    try:
        with open(results_path, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': tester.tests_run,
                    'passed_tests': tester.tests_passed,
                    'failed_tests': tester.tests_run - tester.tests_passed,
                    'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0,
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': tester.test_results
            }, f, indent=2)
    except Exception as e:
        print(f"    ⚠️ Unable to write results to {results_path}: {e}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())