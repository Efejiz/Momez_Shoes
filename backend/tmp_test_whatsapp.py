import requests

BASE = 'http://127.0.0.1:8000/api'
email = 'admin@momezshoes.com'
password = 'Admin123!'

s = requests.Session()

# Login
r = s.post(f'{BASE}/auth/login', json={'email': email, 'password': password})
print('login', r.status_code, r.text)
assert r.status_code == 200, r.text
session = r.json()['session_token']
headers={'Authorization': f'Bearer {session}'}

# Products
rp = s.get(f'{BASE}/products')
print('products', rp.status_code)
prods = rp.json()
assert prods, 'no products'
prod = prods[0]
size = prod['sizes_stock'][0]['size']
print('using product', prod['id'], 'size', size)

# Add to cart
ra = s.post(f'{BASE}/cart/add', headers=headers, json={'product_id': prod['id'], 'size': size, 'quantity': 1})
print('add_to_cart', ra.status_code, ra.text)
assert ra.status_code == 200, ra.text

# Shipping regions
rr = s.get(f'{BASE}/shipping-regions')
print('regions', rr.status_code)
regions = rr.json()
assert regions, 'no regions'
region_id = regions[0]['id']
print('using region', region_id)

# Create order
payload = {
  'shipping_region_id': region_id,
  'customer_name': 'Test Kullanıcı',
  'customer_email': email,
  'customer_phone': '905555555555',
  'shipping_address': 'Test Mah. Cad. No: 1, İstanbul'
}
rorder = s.post(f'{BASE}/orders', headers=headers, json=payload)
print('create_order', rorder.status_code)
print(rorder.text)