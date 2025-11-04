#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = MongoClient(mongo_url)
db = client[db_name]

print("Seeding database...")

# Clear existing data
print("Clearing existing data...")
db.products.delete_many({})
db.shipping_regions.delete_many({})
db.users.delete_many({})

# Create shipping regions
print("Creating shipping regions...")
regions = [
    {
        "id": str(uuid.uuid4()),
        "name": {
            "en": "Local (City)",
            "ar": "محلي (المدينة)",
            "tr": "Yerel (Şehir)"
        },
        "cost": 5.00
    },
    {
        "id": str(uuid.uuid4()),
        "name": {
            "en": "National",
            "ar": "وطني",
            "tr": "Ulusal"
        },
        "cost": 10.00
    },
    {
        "id": str(uuid.uuid4()),
        "name": {
            "en": "International",
            "ar": "دولي",
            "tr": "Uluslararası"
        },
        "cost": 25.00
    }
]
db.shipping_regions.insert_many(regions)

# Create sample products
print("Creating sample products...")
products = [
    # Men's products
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-SHIRT-001",
        "name": {
            "en": "Classic Cotton Shirt",
            "ar": "قميص قطني كلاسيكي",
            "tr": "Klasik Pamuklu Gömlek"
        },
        "description": {
            "en": "Premium cotton shirt with modern fit. Perfect for casual and formal occasions.",
            "ar": "قميص قطني فاخر بقصة عصرية. مثالي للمناسبات غير الرسمية والرسمية.",
            "tr": "Modern kesimli premium pamuklu gömlek. Günlük ve resmi etkinlikler için mükemmel."
        },
        "price": 49.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800"],
        "sizes_stock": [
            {"size": "S", "stock": 10},
            {"size": "M", "stock": 15},
            {"size": "L", "stock": 12},
            {"size": "XL", "stock": 8}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-JEANS-001",
        "name": {
            "en": "Slim Fit Denim Jeans",
            "ar": "جينز دنيم بقصة ضيقة",
            "tr": "Dar Kesim Denim Kot Pantolon"
        },
        "description": {
            "en": "Comfortable slim fit jeans made from high-quality denim. Versatile and durable.",
            "ar": "جينز مريح بقصة ضيقة مصنوع من دنيم عالي الجودة. متعدد الاستخدامات ومتين.",
            "tr": "Yüksek kaliteli denimden yapılmış rahat dar kesim kot pantolon. Çok yönlü ve dayanıklı."
        },
        "price": 79.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1542272604-787c3835535d?w=800"],
        "sizes_stock": [
            {"size": "30", "stock": 8},
            {"size": "32", "stock": 12},
            {"size": "34", "stock": 10},
            {"size": "36", "stock": 6}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-JACKET-001",
        "name": {
            "en": "Leather Bomber Jacket",
            "ar": "سترة بومبر جلدية",
            "tr": "Deri Bomber Ceket"
        },
        "description": {
            "en": "Stylish leather bomber jacket with premium finish. Perfect for cool weather.",
            "ar": "سترة بومبر جلدية أنيقة مع لمسة نهائية فاخرة. مثالية للطقس البارد.",
            "tr": "Premium bitişli şık deri bomber ceket. Serin hava için mükemmel."
        },
        "price": 199.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"],
        "sizes_stock": [
            {"size": "M", "stock": 5},
            {"size": "L", "stock": 7},
            {"size": "XL", "stock": 4}
        ],
        "featured": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # Women's products
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-DRESS-001",
        "name": {
            "en": "Elegant Summer Dress",
            "ar": "فستان صيفي أنيق",
            "tr": "Zarif Yaz Elbisesi"
        },
        "description": {
            "en": "Beautiful floral summer dress with comfortable fit. Perfect for warm days.",
            "ar": "فستان صيفي زهري جميل بقصة مريحة. مثالي للأيام الدافئة.",
            "tr": "Rahat kesimli güzel çiçek desenli yaz elbisesi. Sıcak günler için mükemmel."
        },
        "price": 69.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800"],
        "sizes_stock": [
            {"size": "XS", "stock": 8},
            {"size": "S", "stock": 12},
            {"size": "M", "stock": 10},
            {"size": "L", "stock": 6}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-BLOUSE-001",
        "name": {
            "en": "Silk Blouse",
            "ar": "بلوزة حريرية",
            "tr": "İpek Bluz"
        },
        "description": {
            "en": "Luxurious silk blouse with elegant design. Ideal for office or evening wear.",
            "ar": "بلوزة حريرية فاخرة بتصميم أنيق. مثالية للمكتب أو المناسبات المسائية.",
            "tr": "Zarif tasarımlı lüks ipek bluz. Ofis veya gece kıyafetleri için ideal."
        },
        "price": 89.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800"],
        "sizes_stock": [
            {"size": "S", "stock": 10},
            {"size": "M", "stock": 15},
            {"size": "L", "stock": 8}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-JEANS-001",
        "name": {
            "en": "High-Waist Skinny Jeans",
            "ar": "جينز ضيق بخصر عالي",
            "tr": "Yüksek Bel Skinny Jean"
        },
        "description": {
            "en": "Trendy high-waist skinny jeans with stretch comfort. Flattering fit for all body types.",
            "ar": "جينز ضيق عصري بخصر عالي مع راحة مطاطية. قصة مناسبة لجميع أنواع الجسم.",
            "tr": "Esnek konforlu trend yüksek bel skinny jean. Tüm vücut tipleri için iltifat edici kesim."
        },
        "price": 74.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800"],
        "sizes_stock": [
            {"size": "26", "stock": 8},
            {"size": "28", "stock": 12},
            {"size": "30", "stock": 10},
            {"size": "32", "stock": 5}
        ],
        "featured": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # Sports products
    {
        "id": str(uuid.uuid4()),
        "sku": "SPORT-SHOES-001",
        "name": {
            "en": "Running Shoes Pro",
            "ar": "أحذية الجري برو",
            "tr": "Koşu Ayakkabısı Pro"
        },
        "description": {
            "en": "Professional running shoes with advanced cushioning. Perfect for long-distance running.",
            "ar": "أحذية جري احترافية مع توسيد متقدم. مثالية للجري لمسافات طويلة.",
            "tr": "Gelişmiş yastıklamalı profesyonel koşu ayakkabısı. Uzun mesafe koşusu için mükemmel."
        },
        "price": 129.99,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"],
        "sizes_stock": [
            {"size": "8", "stock": 10},
            {"size": "9", "stock": 15},
            {"size": "10", "stock": 12},
            {"size": "11", "stock": 8}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "SPORT-SHIRT-001",
        "name": {
            "en": "Performance Training T-Shirt",
            "ar": "قميص تدريب الأداء",
            "tr": "Performans Antrenman Tişörtü"
        },
        "description": {
            "en": "Moisture-wicking training shirt with breathable fabric. Keeps you cool during workouts.",
            "ar": "قميص تدريب ماص للرطوبة مع نسيج يسمح بالتنفس. يبقيك باردا أثناء التمارين.",
            "tr": "Nefes alabilir kumaşlı nem emici antrenman tişörtü. Egzersiz sırasında sizi serin tutar."
        },
        "price": 34.99,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800"],
        "sizes_stock": [
            {"size": "S", "stock": 20},
            {"size": "M", "stock": 25},
            {"size": "L", "stock": 18},
            {"size": "XL", "stock": 12}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # New Arrivals
    {
        "id": str(uuid.uuid4()),
        "sku": "NEW-SWEATER-001",
        "name": {
            "en": "Cashmere Blend Sweater",
            "ar": "سترة مزيج الكشمير",
            "tr": "Kaşmir Karışımlı Kazak"
        },
        "description": {
            "en": "Soft cashmere blend sweater with timeless design. Luxurious warmth and comfort.",
            "ar": "سترة مزيج كشمير ناعمة بتصميم خالد. دفء وراحة فاخرة.",
            "tr": "Zamansız tasarımlı yumuşak kaşmir karışımlı kazak. Lüks sıcaklık ve konfor."
        },
        "price": 149.99,
        "category": "new_arrivals",
        "images": ["https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800"],
        "sizes_stock": [
            {"size": "S", "stock": 8},
            {"size": "M", "stock": 10},
            {"size": "L", "stock": 6}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "NEW-COAT-001",
        "name": {
            "en": "Wool Winter Coat",
            "ar": "معطف شتوي صوفي",
            "tr": "Yün Kış Paltosu"
        },
        "description": {
            "en": "Premium wool winter coat with elegant cut. Stay warm in style.",
            "ar": "معطف شتوي صوفي فاخر بقصة أنيقة. ابق دافئا بأناقة.",
            "tr": "Zarif kesimli premium yün kış paltosu. Tarzınızla sıcak kalın."
        },
        "price": 249.99,
        "category": "new_arrivals",
        "images": ["https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800"],
        "sizes_stock": [
            {"size": "M", "stock": 6},
            {"size": "L", "stock": 8},
            {"size": "XL", "stock": 4}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

db.products.insert_many(products)

# Create admin user
print("Creating admin user...")
admin_user = {
    "id": str(uuid.uuid4()),
    "email": "admin@styleshop.com",
    "name": "Admin User",
    "picture": None,
    "role": "admin",
    "created_at": datetime.now(timezone.utc).isoformat()
}
db.users.insert_one(admin_user)

print(f"\n✅ Database seeded successfully!")
print(f"Created {len(products)} products")
print(f"Created {len(regions)} shipping regions")
print(f"Created 1 admin user")
print(f"\nAdmin credentials:")
print(f"Email: admin@styleshop.com")
print(f"Note: Use Google OAuth to login, then manually update the user role to 'admin' in MongoDB")

client.close()
