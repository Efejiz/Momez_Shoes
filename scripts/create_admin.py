"""
Create initial admin user
Email: admin@momezshoes.com
Password: Admin123!
"""
import asyncio
import os
import sys
import bcrypt
import uuid
from datetime import datetime, timezone
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add parent directory to path to import from backend
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def create_admin():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Admin credentials
    admin_email = "admin@momezshoes.com"
    admin_password = "Admin123!"
    admin_name = "Admin"
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": admin_email})
    if existing_admin:
        print(f"✅ Admin user already exists: {admin_email}")
        return
    
    # Hash password
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": admin_email,
        "name": admin_name,
        "picture": None,
        "password": password_hash.decode('utf-8'),  # Store as string
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(admin_user)
    print(f"✅ Admin user created successfully!")
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: {admin_password}")
    print(f"⚠️  Please change the password after first login")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
