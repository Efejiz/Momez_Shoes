#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime, timezone
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

client = MongoClient(mongo_url)
db = client[db_name]

print("Seeding Momez Shoes database...")

# Clear existing products
print("Clearing existing products...")
db.products.delete_many({})

# Create shoe products
print("Creating shoe products...")
products = [
    # Men's Shoes
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-OXFORD-001",
        "name": {
            "en": "Classic Oxford Leather Shoes",
            "ar": "أحذية أوكسفورد جلدية كلاسيكية",
            "tr": "Klasik Oxford Deri Ayakkabı"
        },
        "description": {
            "en": "Premium leather oxford shoes perfect for formal occasions. Handcrafted with attention to detail.",
            "ar": "أحذية أوكسفورد جلدية فاخرة مثالية للمناسبات الرسمية. مصنوعة يدوياً باهتمام بالتفاصيل.",
            "tr": "Resmi etkinlikler için mükemmel premium deri oxford ayakkabı. Detaylara özenle el işçiliği."
        },
        "price": 129.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 12},
            {"size": "41", "stock": 15},
            {"size": "42", "stock": 18},
            {"size": "43", "stock": 14},
            {"size": "44", "stock": 10}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-LOAFER-001",
        "name": {
            "en": "Suede Loafers",
            "ar": "حذاء لوفر من الجلد المدبوغ",
            "tr": "Süet Loafer Ayakkabı"
        },
        "description": {
            "en": "Comfortable suede loafers with cushioned insole. Perfect for casual and semi-formal wear.",
            "ar": "حذاء لوفر مريح من الجلد المدبوغ مع نعل داخلي مبطن. مثالي للارتداء غير الرسمي وشبه الرسمي.",
            "tr": "Yastıklı taban süet loafer ayakkabı. Günlük ve yarı resmi kullanım için mükemmel."
        },
        "price": 89.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 8},
            {"size": "41", "stock": 12},
            {"size": "42", "stock": 15},
            {"size": "43", "stock": 10},
            {"size": "44", "stock": 6}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "MEN-SNEAKER-001",
        "name": {
            "en": "Premium Canvas Sneakers",
            "ar": "أحذية رياضية قماشية فاخرة",
            "tr": "Premium Kanvas Spor Ayakkabı"
        },
        "description": {
            "en": "Stylish canvas sneakers with premium finish. Comfortable for all-day wear.",
            "ar": "أحذية رياضية قماشية أنيقة بلمسة نهائية فاخرة. مريحة للارتداء طوال اليوم.",
            "tr": "Premium bitişli şık kanvas spor ayakkabı. Tüm gün rahat kullanım."
        },
        "price": 69.99,
        "category": "men",
        "images": ["https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 10},
            {"size": "41", "stock": 14},
            {"size": "42", "stock": 16},
            {"size": "43", "stock": 12},
            {"size": "44", "stock": 8}
        ],
        "featured": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # Women's Shoes
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-HEEL-001",
        "name": {
            "en": "Classic Red High Heels",
            "ar": "كعب عالي أحمر كلاسيكي",
            "tr": "Klasik Kırmızı Topuklu Ayakkabı"
        },
        "description": {
            "en": "Elegant red high heels perfect for evening events. Comfortable heel design with cushioned footbed.",
            "ar": "كعب عالي أحمر أنيق مثالي للمناسبات المسائية. تصميم كعب مريح مع قاعدة قدم مبطنة.",
            "tr": "Akşam etkinlikleri için mükemmel zarif kırmızı topuklu ayakkabı. Yastıklı taban ile rahat topuk tasarımı."
        },
        "price": 99.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800"],
        "sizes_stock": [
            {"size": "36", "stock": 10},
            {"size": "37", "stock": 15},
            {"size": "38", "stock": 18},
            {"size": "39", "stock": 12},
            {"size": "40", "stock": 8}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-FLAT-001",
        "name": {
            "en": "Leather Ballet Flats",
            "ar": "أحذية باليه جلدية مسطحة",
            "tr": "Deri Babet Ayakkabı"
        },
        "description": {
            "en": "Soft leather ballet flats for everyday comfort. Versatile design works with any outfit.",
            "ar": "أحذية باليه جلدية ناعمة للراحة اليومية. تصميم متعدد الاستخدامات يتناسب مع أي زي.",
            "tr": "Günlük konfor için yumuşak deri babet ayakkabı. Her kıyafetle uyumlu çok yönlü tasarım."
        },
        "price": 79.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=800"],
        "sizes_stock": [
            {"size": "36", "stock": 12},
            {"size": "37", "stock": 16},
            {"size": "38", "stock": 20},
            {"size": "39", "stock": 14},
            {"size": "40", "stock": 10}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "WOM-BOOT-001",
        "name": {
            "en": "Ankle Boots",
            "ar": "أحذية بوت قصيرة",
            "tr": "Bot Ayakkabı"
        },
        "description": {
            "en": "Trendy ankle boots with block heel. Perfect for fall and winter fashion.",
            "ar": "أحذية بوت قصيرة عصرية مع كعب سميك. مثالية لموضة الخريف والشتاء.",
            "tr": "Kalın topuklu trend bot ayakkabı. Sonbahar ve kış modası için mükemmel."
        },
        "price": 119.99,
        "category": "women",
        "images": ["https://images.unsplash.com/photo-1605733160314-4fc7dac4bb16?w=800"],
        "sizes_stock": [
            {"size": "36", "stock": 8},
            {"size": "37", "stock": 12},
            {"size": "38", "stock": 14},
            {"size": "39", "stock": 10},
            {"size": "40", "stock": 6}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # Sports Shoes
    {
        "id": str(uuid.uuid4()),
        "sku": "SPORT-RUN-001",
        "name": {
            "en": "Professional Running Shoes",
            "ar": "أحذية جري احترافية",
            "tr": "Profesyonel Koşu Ayakkabısı"
        },
        "description": {
            "en": "High-performance running shoes with advanced cushioning technology. Lightweight and breathable.",
            "ar": "أحذية جري عالية الأداء مع تقنية توسيد متقدمة. خفيفة الوزن وقابلة للتنفس.",
            "tr": "Gelişmiş yastıklama teknolojili yüksek performanslı koşu ayakkabısı. Hafif ve nefes alabilir."
        },
        "price": 149.99,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 15},
            {"size": "41", "stock": 20},
            {"size": "42", "stock": 22},
            {"size": "43", "stock": 18},
            {"size": "44", "stock": 12}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "SPORT-TRAIN-001",
        "name": {
            "en": "Cross Training Shoes",
            "ar": "أحذية تدريب شاملة",
            "tr": "Cross Training Ayakkabısı"
        },
        "description": {
            "en": "Versatile training shoes for gym and outdoor activities. Superior grip and stability.",
            "ar": "أحذية تدريب متعددة الاستخدامات للصالة الرياضية والأنشطة الخارجية. قبضة واستقرار فائقان.",
            "tr": "Spor salonu ve açık hava aktiviteleri için çok yönlü antrenman ayakkabısı. Üstün kavrama ve denge."
        },
        "price": 109.99,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 12},
            {"size": "41", "stock": 16},
            {"size": "42", "stock": 18},
            {"size": "43", "stock": 14},
            {"size": "44", "stock": 10}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    # New Arrivals
    {
        "id": str(uuid.uuid4()),
        "sku": "NEW-PREMIUM-001",
        "name": {
            "en": "Limited Edition Designer Sneakers",
            "ar": "أحذية رياضية مصممة إصدار محدود",
            "tr": "Sınırlı Sayıda Tasarımcı Spor Ayakkabı"
        },
        "description": {
            "en": "Exclusive designer sneakers with premium materials. Limited stock available.",
            "ar": "أحذية رياضية حصرية من مصمم مع مواد فاخرة. مخزون محدود متاح.",
            "tr": "Premium malzemeli özel tasarımcı spor ayakkabı. Sınırlı stok mevcut."
        },
        "price": 199.99,
        "category": "new_arrivals",
        "images": ["https://images.unsplash.com/photo-1600185365926-3a2ce3cdb9eb?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 5},
            {"size": "41", "stock": 8},
            {"size": "42", "stock": 10},
            {"size": "43", "stock": 6},
            {"size": "44", "stock": 4}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "sku": "NEW-CASUAL-001",
        "name": {
            "en": "Luxury Casual Shoes",
            "ar": "أحذية كاجوال فاخرة",
            "tr": "Lüks Günlük Ayakkabı"
        },
        "description": {
            "en": "Premium casual shoes with Italian craftsmanship. Comfort meets style.",
            "ar": "أحذية كاجوال فاخرة بحرفية إيطالية. الراحة تلتقي بالأناقة.",
            "tr": "İtalyan işçiliğiyle premium günlük ayakkabı. Konfor ve şıklık bir arada."
        },
        "price": 159.99,
        "category": "new_arrivals",
        "images": ["https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800"],
        "sizes_stock": [
            {"size": "40", "stock": 8},
            {"size": "41", "stock": 10},
            {"size": "42", "stock": 12},
            {"size": "43", "stock": 8},
            {"size": "44", "stock": 5}
        ],
        "featured": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

db.products.insert_many(products)

print(f"\n✅ Momez Shoes database seeded successfully!")
print(f"Created {len(products)} shoe products")
print(f"- Men's Shoes: 3 products")
print(f"- Women's Shoes: 3 products")
print(f"- Sports Shoes: 2 products")
print(f"- New Arrivals: 2 products")

client.close()
