import requests
import json
import uuid

# Test Stripe payment integration
base_url = "https://login-tester-7.preview.emergentagent.com"
api_url = f"{base_url}/api"

print("💳 Testing Stripe Payment Integration")
print("=" * 50)

# Login as admin
login_data = {"email": "admin@momezshoes.com", "password": "Admin123!"}
login_response = requests.post(f"{api_url}/admin/login", json=login_data)

if login_response.status_code != 200:
    print("❌ Failed to login")
    exit(1)

session_token = login_response.json()['session_token']
headers = {'Authorization': f'Bearer {session_token}', 'Content-Type': 'application/json'}

print("✅ Admin logged in successfully")

# Get products
products_response = requests.get(f"{api_url}/products")
if products_response.status_code != 200:
    print("❌ Failed to get products")
    exit(1)

products = products_response.json()
if not products:
    print("❌ No products available")
    exit(1)

print(f"✅ Found {len(products)} products")

# Add item to cart
product = products[0]
cart_data = {
    "product_id": product['id'],
    "size": product['sizes_stock'][0]['size'] if product.get('sizes_stock') else "M",
    "quantity": 1
}

cart_response = requests.post(f"{api_url}/cart/add", json=cart_data, headers=headers)
if cart_response.status_code != 200:
    print(f"❌ Failed to add to cart: {cart_response.status_code} - {cart_response.text}")
    exit(1)

print("✅ Added item to cart")

# Get shipping regions
regions_response = requests.get(f"{api_url}/shipping-regions")
if regions_response.status_code != 200:
    print("❌ Failed to get shipping regions")
    exit(1)

regions = regions_response.json()
if not regions:
    print("❌ No shipping regions available")
    exit(1)

print(f"✅ Found {len(regions)} shipping regions")

# Create order
order_data = {
    "shipping_region_id": regions[0]['id'],
    "customer_name": "Test Customer",
    "customer_email": "test@momezshoes.com",
    "customer_phone": "+90 555 123 4567",
    "shipping_address": "Test Address, Istanbul, Turkey"
}

order_response = requests.post(f"{api_url}/orders", json=order_data, headers=headers)
if order_response.status_code != 200:
    print(f"❌ Failed to create order: {order_response.status_code} - {order_response.text}")
    exit(1)

order = order_response.json()
order_id = order['id']
print(f"✅ Created order: {order_id}")

# Test create checkout session
checkout_data = {
    "order_id": order_id,
    "origin_url": "https://test.example.com"
}

print("\n🔍 Testing checkout session creation...")
checkout_response = requests.post(f"{api_url}/checkout/create-session", json=checkout_data, headers=headers)
print(f"Checkout Status: {checkout_response.status_code}")
print(f"Response: {checkout_response.text[:500]}")

if checkout_response.status_code == 200:
    checkout_result = checkout_response.json()
    session_id = checkout_result.get('session_id')
    if session_id:
        print(f"✅ Checkout session created: {session_id}")
        
        # Test get checkout status
        print("\n🔍 Testing checkout status...")
        status_response = requests.get(f"{api_url}/checkout/status/{session_id}", headers=headers)
        print(f"Status check: {status_response.status_code}")
        print(f"Response: {status_response.text[:300]}")
    else:
        print("❌ No session_id in response")

# Test webhook endpoint
print("\n🔍 Testing webhook endpoint...")
webhook_data = {
    "id": "evt_test_webhook",
    "object": "event",
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_test_session",
            "payment_status": "paid"
        }
    }
}

webhook_response = requests.post(f"{api_url}/webhook/stripe", json=webhook_data)
print(f"Webhook Status: {webhook_response.status_code}")
print(f"Response: {webhook_response.text}")