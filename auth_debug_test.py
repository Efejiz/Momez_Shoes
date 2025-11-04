import requests
import json
import os

# Test authentication behavior
base_url = os.environ.get("BASE_URL", "https://login-tester-7.preview.emergentagent.com")
api_url = f"{base_url}/api"

print("🔍 Testing Authentication Behavior")
print("=" * 50)

# Test 1: Get profile without any authentication
print("\n1. Testing /api/auth/me without authentication:")
response = requests.get(f"{api_url}/auth/me")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

# Test 2: Login as admin
print("\n2. Admin login:")
login_data = {"email": "admin@momezshoes.com", "password": "Admin123!"}
login_response = requests.post(f"{api_url}/admin/login", json=login_data)
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    login_result = login_response.json()
    session_token = login_result.get('session_token')
    print(f"Session token: {session_token[:20]}...")
    
    # Test 3: Use session token with Authorization header
    print("\n3. Testing /api/auth/me with Authorization header:")
    headers = {'Authorization': f'Bearer {session_token}'}
    response = requests.get(f"{api_url}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Test 4: Test without Authorization header (should fail)
    print("\n4. Testing /api/auth/me without Authorization header (after login):")
    response = requests.get(f"{api_url}/auth/me")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Test 5: Test admin endpoint without auth
    print("\n5. Testing /api/admin/orders without Authorization header:")
    response = requests.get(f"{api_url}/admin/orders")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    # Test 6: Test admin endpoint with auth
    print("\n6. Testing /api/admin/orders with Authorization header:")
    response = requests.get(f"{api_url}/admin/orders", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

else:
    print(f"Login failed: {login_response.text}")