from fastapi import FastAPI, APIRouter, HTTPException, Cookie, Response, Depends, UploadFile, File, Form, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import requests
import aiofiles
import shutil
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Upload folder for product images
UPLOAD_FOLDER = Path("/app/frontend/public/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Enums
class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"

class ProductCategory(str, Enum):
    men = "men"
    women = "women"
    sports = "sports"
    new_arrivals = "new_arrivals"

# Pydantic Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: Optional[str] = None
    password: Optional[str] = None  # Only for admin users
    role: UserRole = UserRole.customer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SizeStock(BaseModel):
    size: str
    stock: int

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku: str
    name: Dict[str, str]  # {"en": "...", "ar": "...", "tr": "..."}
    description: Dict[str, str]
    price: float
    category: ProductCategory
    images: List[str] = []  # URLs or paths
    sizes_stock: List[SizeStock] = []
    featured: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_id: str
    size: str
    quantity: int

class Cart(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ShippingRegion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Dict[str, str]
    cost: float

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    size: str
    quantity: int
    price: float

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_cost: float
    shipping_region: str
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    status: OrderStatus = OrderStatus.pending
    payment_method: str = "COD"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class SessionDataResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str]
    session_token: str

class AddToCartRequest(BaseModel):
    product_id: str
    size: str
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    shipping_region_id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str

class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus

class ProductCreateRequest(BaseModel):
    sku: str
    name_en: str
    name_ar: str
    name_tr: str
    description_en: str
    description_ar: str
    description_tr: str
    price: float
    category: ProductCategory
    sizes_stock: List[SizeStock]
    featured: bool = False

class AdminLoginRequest(BaseModel):
    email: str
    password: str

# Auth Helper
async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = None) -> Optional[User]:
    token = session_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
    
    if not token:
        return None
    
    session = await db.user_sessions.find_one({"session_token": token})
    if not session or datetime.fromisoformat(session['expires_at']) < datetime.now(timezone.utc):
        return None
    
    user_doc = await db.users.find_one({"id": session["user_id"]})
    if not user_doc:
        return None
    
    return User(**user_doc)

async def require_auth(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)) -> User:
    user = await get_current_user(session_token, authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

async def require_admin(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)) -> User:
    user = await require_auth(session_token, authorization)
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Routes
@api_router.get("/")
async def root():
    return {"message": "E-commerce API"}

# Auth Routes
@api_router.get("/auth/session-data")
async def get_session_data(x_session_id: Optional[str] = None) -> SessionDataResponse:
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing session ID")
    
    # Call Emergent Auth API
    try:
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": x_session_id}
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get session data: {str(e)}")
    
    # Create or get user
    user_doc = await db.users.find_one({"email": data["email"]})
    if not user_doc:
        user = User(
            id=str(uuid.uuid4()),
            email=data["email"],
            name=data["name"],
            picture=data.get("picture"),
            role=UserRole.customer
        )
        user_dict = user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        await db.users.insert_one(user_dict)
    else:
        user = User(**user_doc)
    
    # Create session
    session_token = data["session_token"]
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    session_dict = session.model_dump()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    await db.user_sessions.insert_one(session_dict)
    
    return SessionDataResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        session_token=session_token
    )

@api_router.get("/auth/me")
async def get_me(user: User = Depends(require_auth)):
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, user: User = Depends(require_auth), session_token: Optional[str] = Cookie(None)):
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie("session_token")
    return {"message": "Logged out"}

@api_router.post("/admin/login")
async def admin_login(request: AdminLoginRequest) -> SessionDataResponse:
    # Find admin user by email
    user_doc = await db.users.find_one({"email": request.email, "role": "admin"})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    user = User(**user_doc)
    stored_password = user_doc.get("password")
    if not stored_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if password matches
    if not bcrypt.checkpw(request.password.encode('utf-8'), stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create session
    session_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    session_dict = session.model_dump()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    await db.user_sessions.insert_one(session_dict)
    
    return SessionDataResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        session_token=session_token
    )

# Product Routes
@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, featured: Optional[bool] = None):
    query = {}
    if category:
        query["category"] = category
    if featured is not None:
        query["featured"] = featured
    
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Cart Routes
@api_router.get("/cart")
async def get_cart(user: User = Depends(require_auth)):
    cart = await db.carts.find_one({"user_id": user.id}, {"_id": 0})
    if not cart:
        return {"items": []}
    return cart

@api_router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest, user: User = Depends(require_auth)):
    # Check product exists and has stock
    product = await db.products.find_one({"id": request.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    size_stock = next((s for s in product["sizes_stock"] if s["size"] == request.size), None)
    if not size_stock or size_stock["stock"] < request.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart:
        cart = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "items": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.carts.insert_one(cart)
    
    # Check if item exists in cart
    existing_item = next((item for item in cart["items"] if item["product_id"] == request.product_id and item["size"] == request.size), None)
    if existing_item:
        existing_item["quantity"] += request.quantity
    else:
        cart["items"].append({
            "product_id": request.product_id,
            "size": request.size,
            "quantity": request.quantity
        })
    
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.carts.update_one({"user_id": user.id}, {"$set": cart})
    
    return {"message": "Added to cart"}

@api_router.delete("/cart/remove/{product_id}/{size}")
async def remove_from_cart(product_id: str, size: str, user: User = Depends(require_auth)):
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart["items"] = [item for item in cart["items"] if not (item["product_id"] == product_id and item["size"] == size)]
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.carts.update_one({"user_id": user.id}, {"$set": cart})
    
    return {"message": "Removed from cart"}

@api_router.post("/cart/clear")
async def clear_cart(user: User = Depends(require_auth)):
    await db.carts.update_one({"user_id": user.id}, {"$set": {"items": [], "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Cart cleared"}

# Order Routes
@api_router.post("/orders")
async def create_order(request: CreateOrderRequest, user: User = Depends(require_auth)):
    # Get cart
    cart = await db.carts.find_one({"user_id": user.id})
    if not cart or not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Get shipping region
    region = await db.shipping_regions.find_one({"id": request.shipping_region_id})
    if not region:
        raise HTTPException(status_code=404, detail="Shipping region not found")
    
    # Calculate order
    order_items = []
    total_amount = 0
    
    for cart_item in cart["items"]:
        product = await db.products.find_one({"id": cart_item["product_id"]})
        if not product:
            continue
        
        # Check stock
        size_stock = next((s for s in product["sizes_stock"] if s["size"] == cart_item["size"]), None)
        if not size_stock or size_stock["stock"] < cart_item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']['en']}")
        
        order_items.append(OrderItem(
            product_id=product["id"],
            product_name=product["name"]["en"],
            size=cart_item["size"],
            quantity=cart_item["quantity"],
            price=product["price"]
        ))
        total_amount += product["price"] * cart_item["quantity"]
        
        # Update stock
        for size_s in product["sizes_stock"]:
            if size_s["size"] == cart_item["size"]:
                size_s["stock"] -= cart_item["quantity"]
        await db.products.update_one({"id": product["id"]}, {"$set": {"sizes_stock": product["sizes_stock"]}})
    
    # Create order
    order = Order(
        id=str(uuid.uuid4()),
        user_id=user.id,
        items=[item.model_dump() for item in order_items],
        total_amount=total_amount,
        shipping_cost=region["cost"],
        shipping_region=region["name"]["en"],
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        shipping_address=request.shipping_address,
        status=OrderStatus.pending,
        payment_method="COD"
    )
    
    order_dict = order.model_dump()
    order_dict['created_at'] = order_dict['created_at'].isoformat()
    order_dict['updated_at'] = order_dict['updated_at'].isoformat()
    await db.orders.insert_one(order_dict)
    
    # Clear cart
    await db.carts.update_one({"user_id": user.id}, {"$set": {"items": []}})
    
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders(user: User = Depends(require_auth)):
    orders = await db.orders.find({"user_id": user.id}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, user: User = Depends(require_auth)):
    order = await db.orders.find_one({"id": order_id, "user_id": user.id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Shipping Regions
@api_router.get("/shipping-regions", response_model=List[ShippingRegion])
async def get_shipping_regions():
    regions = await db.shipping_regions.find({}, {"_id": 0}).to_list(100)
    return regions

# Admin Routes
@api_router.post("/admin/products")
async def create_product(request: ProductCreateRequest, user: User = Depends(require_admin)):
    product = Product(
        id=str(uuid.uuid4()),
        sku=request.sku,
        name={
            "en": request.name_en,
            "ar": request.name_ar,
            "tr": request.name_tr
        },
        description={
            "en": request.description_en,
            "ar": request.description_ar,
            "tr": request.description_tr
        },
        price=request.price,
        category=request.category,
        sizes_stock=[s.model_dump() for s in request.sizes_stock],
        featured=request.featured,
        images=[]
    )
    
    product_dict = product.model_dump()
    product_dict['created_at'] = product_dict['created_at'].isoformat()
    await db.products.insert_one(product_dict)
    
    return product

@api_router.put("/admin/products/{product_id}")
async def update_product(product_id: str, request: ProductCreateRequest, user: User = Depends(require_admin)):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {
        "sku": request.sku,
        "name": {
            "en": request.name_en,
            "ar": request.name_ar,
            "tr": request.name_tr
        },
        "description": {
            "en": request.description_en,
            "ar": request.description_ar,
            "tr": request.description_tr
        },
        "price": request.price,
        "category": request.category,
        "sizes_stock": [s.model_dump() for s in request.sizes_stock],
        "featured": request.featured
    }
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    return {"message": "Product updated"}

@api_router.delete("/admin/products/{product_id}")
async def delete_product(product_id: str, user: User = Depends(require_admin)):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

@api_router.post("/admin/products/{product_id}/images")
async def upload_product_image(product_id: str, file: UploadFile = File(...), user: User = Depends(require_admin)):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_FOLDER / filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update product
    image_url = f"/uploads/{filename}"
    product["images"].append(image_url)
    await db.products.update_one({"id": product_id}, {"$set": {"images": product["images"]}})
    
    return {"message": "Image uploaded", "url": image_url}

@api_router.get("/admin/orders", response_model=List[Order])
async def get_all_orders(user: User = Depends(require_admin)):
    orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.patch("/admin/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateOrderStatusRequest, user: User = Depends(require_admin)):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": request.status.value, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # TODO: Send notification (mocked for now)
    
    return {"message": "Order status updated"}

@api_router.get("/admin/reports/best-selling")
async def get_best_selling_products(user: User = Depends(require_admin)):
    # Aggregate orders to find best-selling products
    pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "product_name": {"$first": "$items.product_name"},
                "total_quantity": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
            }
        },
        {"$sort": {"total_quantity": -1}},
        {"$limit": 10}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(10)
    return results

@api_router.get("/admin/reports/regions")
async def get_active_regions(user: User = Depends(require_admin)):
    # Aggregate orders by shipping region
    pipeline = [
        {
            "$group": {
                "_id": "$shipping_region",
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"}
            }
        },
        {"$sort": {"total_orders": -1}}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(100)
    return results

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
