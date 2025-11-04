from fastapi import FastAPI, APIRouter, HTTPException, Cookie, Response, Depends, UploadFile, File, Form, Header, Request, Body
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

class PaymentStatus(str, Enum):
    pending = "pending"
    initiated = "initiated"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class ReviewRating(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5

class CouponType(str, Enum):
    percentage = "percentage"
    fixed = "fixed"

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
    remember_me: bool = False
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

# New Models for Enhanced Features

class UserAddress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "TR"
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_id: Optional[str] = None
    session_id: str
    amount: float
    currency: str = "usd"
    payment_status: PaymentStatus = PaymentStatus.pending
    stripe_payment_intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PasswordResetToken(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models for New Features

class AddAddressRequest(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "TR"
    is_default: bool = False

# Allow partial updates in PUT without 422
class UpdateAddressRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: str

class ConfirmPasswordResetRequest(BaseModel):
    token: str
    new_password: str

class SearchProductsRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "created_at"  # created_at, price_asc, price_desc, name
    page: int = 1
    limit: int = 20

class CheckoutSessionRequest(BaseModel):
    order_id: str
    origin_url: str

# Email/Password Registration Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

# Review Models
class ProductReview(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    user_name: str
    rating: int  # 1-5
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AddReviewRequest(BaseModel):
    product_id: str
    rating: int
    comment: str

# Wishlist Model
class WishlistItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    product_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Coupon Model
class Coupon(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    type: CouponType
    value: float  # percentage or fixed amount
    min_purchase: Optional[float] = None
    max_discount: Optional[float] = None
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None
    used_count: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApplyCouponRequest(BaseModel):
    code: str

class CreateCouponRequest(BaseModel):
    code: str
    type: CouponType
    value: float
    min_purchase: Optional[float] = None
    max_discount: Optional[float] = None
    expires_at: Optional[str] = None
    usage_limit: Optional[int] = None

# Shipping Tracking Model
class ShippingTracking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    tracking_number: str
    carrier: str
    status: str
    estimated_delivery: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UpdateTrackingRequest(BaseModel):
    tracking_number: str
    carrier: str
    status: str
    estimated_delivery: Optional[str] = None

# Contact Form Model
class ContactMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    subject: str
    message: str
    status: str = "new"  # new, read, replied
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactFormRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

# Return/Refund Model
class OrderReturn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    user_id: str
    reason: str
    status: str = "requested"  # requested, approved, rejected, completed
    refund_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RequestReturnRequest(BaseModel):
    order_id: str
    reason: str


class AdminLoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

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
async def get_session_data(response: Response, x_session_id: Optional[str] = Header(None, alias="X-Session-ID")) -> SessionDataResponse:
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing session ID")
    
    # Call Emergent Auth API
    try:
        oauth_resp = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": x_session_id}
        )
        oauth_resp.raise_for_status()
        data = oauth_resp.json()
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

    # Set httpOnly cookie for OAuth session
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600
    )
    
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
async def logout(response: Response, user: User = Depends(require_auth), session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    token = session_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    response.delete_cookie("session_token")
    return {"message": "Logged out"}

@api_router.post("/admin/login")
async def admin_login(request: AdminLoginRequest, response: Response) -> SessionDataResponse:
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
    expires_days = 30 if request.remember_me else 7
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        remember_me=request.remember_me
    )
    session_dict = session.model_dump()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    await db.user_sessions.insert_one(session_dict)

    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=expires_days * 24 * 3600
    )
    
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

    # WhatsApp notification (optional)
    try:
        if os.environ.get('WHATSAPP_ENABLED', 'false').lower() == 'true' and order.customer_phone:
            token = os.environ.get('WHATSAPP_TOKEN')
            phone_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
            if token and phone_id:
                url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                total = order.total_amount + order.shipping_cost
                body = (
                    f"Merhaba {order.customer_name}, siparişiniz alındı.\\n"
                    f"Sipariş No: {order.id}\\n"
                    f"Toplam: {total:.2f}₺\\n"
                    f"Kargo Bölgesi: {order.shipping_region}\\n"
                    f"Adres: {order.shipping_address}\\n"
                    f"Durum: {order.status}"
                )
                payload = {
                    "messaging_product": "whatsapp",
                    "to": order.customer_phone,
                    "type": "text",
                    "text": {"preview_url": False, "body": body}
                }
                resp = requests.post(url, headers=headers, json=payload, timeout=10)
                logging.getLogger(__name__).info("WhatsApp send status %s: %s", resp.status_code, resp.text)
            else:
                logging.getLogger(__name__).warning("WhatsApp env vars missing; skip notify")
    except Exception as e:
        logging.getLogger(__name__).exception("WhatsApp notify failed: %s", e)
    
    # Clear cart
    await db.carts.update_one({"user_id": user.id}, {"$set": {"items": []}})
    
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders(user: User = Depends(require_auth)):
    orders = await db.orders.find({"user_id": user.id}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.get("/orders/returns")
async def get_user_returns(user: User = Depends(require_auth)):
    returns = await db.order_returns.find({"user_id": user.id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return returns

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

# ===== NEW FEATURES API ENDPOINTS =====

# 1. USER PROFILE & ADDRESS MANAGEMENT
@api_router.get("/profile/addresses")
async def get_user_addresses(user: User = Depends(require_auth)):
    addresses = await db.user_addresses.find({"user_id": user.id}, {"_id": 0}).to_list(100)
    return addresses

@api_router.get("/profile/addresses/{address_id}")
async def get_address(address_id: str, user: User = Depends(require_auth)):
    address = await db.user_addresses.find_one({"id": address_id, "user_id": user.id}, {"_id": 0})
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@api_router.post("/profile/addresses")
async def add_address(request: AddAddressRequest, user: User = Depends(require_auth)):
    # If this is default, unset other defaults
    if request.is_default:
        await db.user_addresses.update_many(
            {"user_id": user.id},
            {"$set": {"is_default": False}}
        )
    
    address = UserAddress(
        id=str(uuid.uuid4()),
        user_id=user.id,
        **request.model_dump()
    )
    address_dict = address.model_dump()
    address_dict['created_at'] = address_dict['created_at'].isoformat()
    await db.user_addresses.insert_one(address_dict)
    return address

@api_router.put("/profile/addresses/{address_id}")
async def update_address(address_id: str, request: Optional[UpdateAddressRequest] = Body(None), user: User = Depends(require_auth)):
    address = await db.user_addresses.find_one({"id": address_id, "user_id": user.id})
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, unset other defaults
    if request and request.is_default:
        await db.user_addresses.update_many(
            {"user_id": user.id, "id": {"$ne": address_id}},
            {"$set": {"is_default": False}}
        )
    
    update_data = request.model_dump(exclude_none=True) if request else {}
    if not update_data:
        return {"message": "No changes"}
    
    await db.user_addresses.update_one(
        {"id": address_id},
        {"$set": update_data}
    )
    return {"message": "Address updated"}

@api_router.delete("/profile/addresses/{address_id}")
async def delete_address(address_id: str, user: User = Depends(require_auth)):
    result = await db.user_addresses.delete_one({"id": address_id, "user_id": user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted"}

# 2. PASSWORD MANAGEMENT
@api_router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, user: User = Depends(require_auth)):
    # Get user with password
    user_doc = await db.users.find_one({"id": user.id})
    if not user_doc or not user_doc.get("password"):
        raise HTTPException(status_code=400, detail="Password change not available for this account")
    
    # Verify old password
    stored_password = user_doc.get("password")
    if not bcrypt.checkpw(request.old_password.encode('utf-8'), stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Hash new password
    new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Update password
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"password": new_password_hash.decode('utf-8')}}
    )
    
    return {"message": "Password changed successfully"}

@api_router.post("/auth/reset-password")
async def request_password_reset(request: ResetPasswordRequest):
    # Find user
    user_doc = await db.users.find_one({"email": request.email, "role": "admin"})
    if not user_doc:
        # Don't reveal if user exists
        return {"message": "If the email exists, a reset link will be sent"}
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    token_data = PasswordResetToken(
        id=str(uuid.uuid4()),
        user_id=user_doc["id"],
        token=reset_token,
        expires_at=expires_at
    )
    token_dict = token_data.model_dump()
    token_dict['expires_at'] = token_dict['expires_at'].isoformat()
    token_dict['created_at'] = token_dict['created_at'].isoformat()
    await db.password_reset_tokens.insert_one(token_dict)
    
    # TODO: Send email with reset link
    # For now, return token (in production, send via email)
    logger.info(f"Password reset token for {request.email}: {reset_token}")
    
    return {"message": "If the email exists, a reset link will be sent"}

@api_router.post("/auth/confirm-reset-password")
async def confirm_password_reset(request: ConfirmPasswordResetRequest):
    # Find valid token
    token_doc = await db.password_reset_tokens.find_one({
        "token": request.token,
        "used": False
    })
    
    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check expiration
    expires_at = datetime.fromisoformat(token_doc['expires_at'])
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Hash new password
    new_password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Update password
    await db.users.update_one(
        {"id": token_doc["user_id"]},
        {"$set": {"password": new_password_hash.decode('utf-8')}}
    )
    
    # Mark token as used
    await db.password_reset_tokens.update_one(
        {"token": request.token},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password reset successful"}

# 3. PRODUCT SEARCH AND FILTERING
@api_router.post("/products/search")
async def search_products(request: SearchProductsRequest):
    # Build query
    query = {}
    
    # Text search
    if request.query:
        # Search in product names across all languages
        query["$or"] = [
            {"name.en": {"$regex": request.query, "$options": "i"}},
            {"name.ar": {"$regex": request.query, "$options": "i"}},
            {"name.tr": {"$regex": request.query, "$options": "i"}},
            {"sku": {"$regex": request.query, "$options": "i"}}
        ]
    
    # Category filter
    if request.category:
        query["category"] = request.category
    
    # Price range filter
    if request.min_price is not None or request.max_price is not None:
        query["price"] = {}
        if request.min_price is not None:
            query["price"]["$gte"] = request.min_price
        if request.max_price is not None:
            query["price"]["$lte"] = request.max_price
    
    # Sorting
    sort_options = {
        "created_at": ("created_at", -1),
        "price_asc": ("price", 1),
        "price_desc": ("price", -1),
        "name": ("name.en", 1)
    }
    sort_field, sort_order = sort_options.get(request.sort_by, ("created_at", -1))
    
    # Pagination
    skip = (request.page - 1) * request.limit
    
    # Get total count
    total = await db.products.count_documents(query)
    
    # Get products
    products = await db.products.find(query, {"_id": 0}) \
        .sort(sort_field, sort_order) \
        .skip(skip) \
        .limit(request.limit) \
        .to_list(request.limit)
    
    return {
        "products": products,
        "total": total,
        "page": request.page,
        "limit": request.limit,
        "total_pages": (total + request.limit - 1) // request.limit
    }

# 4. STRIPE PAYMENT INTEGRATION
@api_router.post("/checkout/create-session")
async def create_checkout_session(request: CheckoutSessionRequest, user: User = Depends(require_auth), http_request: Request = None):
    # Get order
    order = await db.orders.find_one({"id": request.order_id, "user_id": user.id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if already paid
    if order.get("payment_status") == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    try:
        # Import Stripe integration
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest as StripeRequest
        
        # Get Stripe API key
        stripe_api_key = os.getenv('STRIPE_API_KEY', 'sk_test_emergent')
        
        # Create webhook URL
        webhook_url = f"{request.origin_url}/api/webhook/stripe"
        
        # Initialize Stripe
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Calculate total amount (order total + shipping)
        total_amount = order["total_amount"] + order["shipping_cost"]
        
        # Create success and cancel URLs
        success_url = f"{request.origin_url}/order-success?session_id={{{{CHECKOUT_SESSION_ID}}}}"
        cancel_url = f"{request.origin_url}/checkout"
        
        # Create checkout session
        checkout_request = StripeRequest(
            amount=float(total_amount),
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": order["id"],
                "user_id": user.id,
                "user_email": user.email
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction
        payment = PaymentTransaction(
            id=str(uuid.uuid4()),
            user_id=user.id,
            order_id=order["id"],
            session_id=session.session_id,
            amount=total_amount,
            currency="usd",
            payment_status=PaymentStatus.initiated,
            metadata=checkout_request.metadata
        )
        payment_dict = payment.model_dump()
        payment_dict['created_at'] = payment_dict['created_at'].isoformat()
        payment_dict['updated_at'] = payment_dict['updated_at'].isoformat()
        await db.payment_transactions.insert_one(payment_dict)
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, user: User = Depends(require_auth)):
    # Get payment transaction
    payment = await db.payment_transactions.find_one({"session_id": session_id, "user_id": user.id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    try:
        # Import Stripe integration
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_api_key = os.getenv('STRIPE_API_KEY', 'sk_test_emergent')
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        # Get checkout status from Stripe
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update payment transaction if status changed
        if status.payment_status == "paid" and payment["payment_status"] != PaymentStatus.completed:
            # Update payment
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": PaymentStatus.completed,
                    "stripe_payment_intent": status.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Update order
            await db.orders.update_one(
                {"id": payment["order_id"]},
                {"$set": {
                    "payment_method": "stripe",
                    "payment_status": "paid",
                    "status": OrderStatus.processing
                }}
            )
            
            # TODO: Send order confirmation email
            logger.info(f"Order {payment['order_id']} paid successfully")
        
        return {
            "payment_status": status.payment_status,
            "amount": status.amount_total / 100,  # Convert from cents
            "currency": status.currency,
            "order_id": payment.get("order_id")
        }
        
    except Exception as e:
        logger.error(f"Checkout status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get checkout status")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        stripe_api_key = os.getenv('STRIPE_API_KEY', 'sk_test_emergent')
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
        
        # Handle webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process webhook based on event type
        if webhook_response.event_type == "checkout.session.completed":
            session_id = webhook_response.session_id
            
            # Update payment transaction
            payment = await db.payment_transactions.find_one({"session_id": session_id})
            if payment and payment["payment_status"] != PaymentStatus.completed:
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "payment_status": PaymentStatus.completed,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                # Update order
                if payment.get("order_id"):
                    await db.orders.update_one(
                        {"id": payment["order_id"]},
                        {"$set": {
                            "payment_method": "stripe",
                            "payment_status": "paid",
                            "status": OrderStatus.processing
                        }}
                    )
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

# 6. EMAIL/PASSWORD REGISTRATION & LOGIN
@api_router.post("/auth/register")
async def register_user(request: RegisterRequest):
    # Check if user exists
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        name=request.name,
        password=password_hash.decode('utf-8'),
        role=UserRole.customer
    )
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await db.users.insert_one(user_dict)
    
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

@api_router.post("/auth/login")
async def login_user(request: LoginRequest, response: Response):
    # Find user (allow both customer and admin)
    user_doc = await db.users.find_one({"email": request.email})
    if not user_doc or not user_doc.get("password"):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    stored_password = user_doc.get("password")
    if not bcrypt.checkpw(request.password.encode('utf-8'), stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_doc)
    
    # Create session
    session_token = str(uuid.uuid4())
    expires_days = 30 if request.remember_me else 7
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        remember_me=request.remember_me
    )
    session_dict = session.model_dump()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    await db.user_sessions.insert_one(session_dict)

    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=expires_days * 24 * 3600
    )
    
    return SessionDataResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        session_token=session_token
    )

# 7. PRODUCT REVIEWS & RATINGS
@api_router.get("/products/{product_id}/reviews")
async def get_product_reviews(product_id: str):
    reviews = await db.product_reviews.find({"product_id": product_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return reviews

@api_router.post("/products/reviews")
async def add_review(request: AddReviewRequest, user: User = Depends(require_auth)):
    # Check if user already reviewed
    existing = await db.product_reviews.find_one({"product_id": request.product_id, "user_id": user.id})
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this product")
    
    # Validate rating
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review = ProductReview(
        id=str(uuid.uuid4()),
        product_id=request.product_id,
        user_id=user.id,
        user_name=user.name,
        rating=request.rating,
        comment=request.comment
    )
    review_dict = review.model_dump()
    review_dict['created_at'] = review_dict['created_at'].isoformat()
    await db.product_reviews.insert_one(review_dict)
    
    return review

@api_router.get("/products/{product_id}/rating")
async def get_product_rating(product_id: str):
    # Calculate average rating
    pipeline = [
        {"$match": {"product_id": product_id}},
        {"$group": {
            "_id": "$product_id",
            "average_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    result = await db.product_reviews.aggregate(pipeline).to_list(1)
    if result:
        return {
            "average_rating": round(result[0]["average_rating"], 1),
            "total_reviews": result[0]["total_reviews"]
        }
    return {"average_rating": 0, "total_reviews": 0}

# 8. WISHLIST
@api_router.get("/wishlist")
async def get_wishlist(user: User = Depends(require_auth)):
    wishlist = await db.wishlist.find({"user_id": user.id}, {"_id": 0}).to_list(100)
    # Get product details
    product_ids = [item["product_id"] for item in wishlist]
    products = await db.products.find({"id": {"$in": product_ids}}, {"_id": 0}).to_list(100)
    return {"items": wishlist, "products": products}

@api_router.post("/wishlist/add/{product_id}")
async def add_to_wishlist(product_id: str, user: User = Depends(require_auth)):
    # Check if already in wishlist
    existing = await db.wishlist.find_one({"user_id": user.id, "product_id": product_id})
    if existing:
        raise HTTPException(status_code=400, detail="Product already in wishlist")
    
    item = WishlistItem(
        id=str(uuid.uuid4()),
        user_id=user.id,
        product_id=product_id
    )
    item_dict = item.model_dump()
    item_dict['created_at'] = item_dict['created_at'].isoformat()
    await db.wishlist.insert_one(item_dict)
    
    return {"message": "Added to wishlist"}

@api_router.delete("/wishlist/remove/{product_id}")
async def remove_from_wishlist(product_id: str, user: User = Depends(require_auth)):
    result = await db.wishlist.delete_one({"user_id": user.id, "product_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    return {"message": "Removed from wishlist"}

# 9. COUPON SYSTEM
@api_router.post("/coupons/apply")
async def apply_coupon(request: ApplyCouponRequest, user: User = Depends(require_auth)):
    # Find coupon
    coupon_doc = await db.coupons.find_one({"code": request.code.upper(), "active": True})
    if not coupon_doc:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    
    coupon = Coupon(**coupon_doc)
    
    # Check expiration
    if coupon.expires_at:
        if isinstance(coupon.expires_at, datetime):
            expires_at = coupon.expires_at
        else:
            expires_at = datetime.fromisoformat(coupon.expires_at)
        
        # Ensure both datetimes are timezone-aware for comparison
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Coupon has expired")
    
    # Check usage limit
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    return coupon

@api_router.post("/admin/coupons")
async def create_coupon(request: CreateCouponRequest, user: User = Depends(require_admin)):
    # Check if code exists
    existing = await db.coupons.find_one({"code": request.code.upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    coupon = Coupon(
        id=str(uuid.uuid4()),
        code=request.code.upper(),
        type=request.type,
        value=request.value,
        min_purchase=request.min_purchase,
        max_discount=request.max_discount,
        expires_at=datetime.fromisoformat(request.expires_at) if request.expires_at else None,
        usage_limit=request.usage_limit
    )
    coupon_dict = coupon.model_dump()
    if coupon_dict.get('expires_at'):
        coupon_dict['expires_at'] = coupon_dict['expires_at'].isoformat()
    coupon_dict['created_at'] = coupon_dict['created_at'].isoformat()
    await db.coupons.insert_one(coupon_dict)
    
    return coupon

@api_router.get("/admin/coupons")
async def get_all_coupons(user: User = Depends(require_admin)):
    coupons = await db.coupons.find({}, {"_id": 0}).to_list(100)
    return coupons

# 10. SHIPPING TRACKING
@api_router.post("/admin/orders/{order_id}/tracking")
async def update_shipping_tracking(order_id: str, request: UpdateTrackingRequest, user: User = Depends(require_admin)):
    # Check if order exists
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Create or update tracking
    tracking = ShippingTracking(
        id=str(uuid.uuid4()),
        order_id=order_id,
        tracking_number=request.tracking_number,
        carrier=request.carrier,
        status=request.status,
        estimated_delivery=datetime.fromisoformat(request.estimated_delivery) if request.estimated_delivery else None
    )
    
    tracking_dict = tracking.model_dump()
    if tracking_dict.get('estimated_delivery'):
        tracking_dict['estimated_delivery'] = tracking_dict['estimated_delivery'].isoformat()
    tracking_dict['updated_at'] = tracking_dict['updated_at'].isoformat()
    
    # Upsert tracking info
    await db.shipping_tracking.update_one(
        {"order_id": order_id},
        {"$set": tracking_dict},
        upsert=True
    )
    
    return {"message": "Tracking info updated"}

@api_router.get("/orders/{order_id}/tracking")
async def get_tracking_info(order_id: str, user: User = Depends(require_auth)):
    # Verify order belongs to user
    order = await db.orders.find_one({"id": order_id, "user_id": user.id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    tracking = await db.shipping_tracking.find_one({"order_id": order_id}, {"_id": 0})
    if not tracking:
        return {"message": "No tracking information available"}
    
    return tracking

# 11. ORDER RETURN/REFUND
@api_router.post("/orders/return")
async def request_return(request: RequestReturnRequest, user: User = Depends(require_auth)):
    # Verify order belongs to user
    order = await db.orders.find_one({"id": request.order_id, "user_id": user.id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if already requested
    existing = await db.order_returns.find_one({"order_id": request.order_id})
    if existing:
        raise HTTPException(status_code=400, detail="Return already requested for this order")
    
    order_return = OrderReturn(
        id=str(uuid.uuid4()),
        order_id=request.order_id,
        user_id=user.id,
        reason=request.reason,
        refund_amount=order["total_amount"] + order["shipping_cost"]
    )
    return_dict = order_return.model_dump()
    return_dict['created_at'] = return_dict['created_at'].isoformat()
    return_dict['updated_at'] = return_dict['updated_at'].isoformat()
    await db.order_returns.insert_one(return_dict)
    
    return {"message": "Return request submitted", "return_id": order_return.id}

@api_router.get("/admin/returns")
async def get_all_returns(user: User = Depends(require_admin)):
    returns = await db.order_returns.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return returns

@api_router.patch("/admin/returns/{return_id}/status")
async def update_return_status(return_id: str, status: str, user: User = Depends(require_admin)):
    result = await db.order_returns.update_one(
        {"id": return_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Return request not found")
    return {"message": "Return status updated"}

# 12. CONTACT FORM
@api_router.post("/contact")
async def submit_contact_form(request: ContactFormRequest):
    message = ContactMessage(
        id=str(uuid.uuid4()),
        name=request.name,
        email=request.email,
        subject=request.subject,
        message=request.message
    )
    message_dict = message.model_dump()
    message_dict['created_at'] = message_dict['created_at'].isoformat()
    await db.contact_messages.insert_one(message_dict)
    
    return {"message": "Message sent successfully"}

@api_router.get("/admin/contacts")
async def get_contact_messages(user: User = Depends(require_admin)):
    messages = await db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return messages

@api_router.patch("/admin/contacts/{message_id}/status")
async def update_contact_status(message_id: str, status: str, user: User = Depends(require_admin)):
    result = await db.contact_messages.update_one(
        {"id": message_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Status updated"}

# 13. ADMIN ANALYTICS
@api_router.get("/admin/analytics/dashboard")
async def get_dashboard_analytics(user: User = Depends(require_admin)):
    # Total orders
    total_orders = await db.orders.count_documents({})
    
    # Total revenue
    revenue_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    revenue_result = await db.orders.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    # Total customers
    total_customers = await db.users.count_documents({"role": "customer"})
    
    # Pending orders
    pending_orders = await db.orders.count_documents({"status": "pending"})
    
    # Low stock products
    all_products = await db.products.find({}, {"_id": 0}).to_list(1000)
    low_stock = []
    for product in all_products:
        for size_stock in product.get("sizes_stock", []):
            if size_stock["stock"] < 5:
                low_stock.append({
                    "product_id": product["id"],
                    "product_name": product["name"]["en"],
                    "size": size_stock["size"],
                    "stock": size_stock["stock"]
                })
    
    # Recent orders
    recent_orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "pending_orders": pending_orders,
        "low_stock_products": low_stock,
        "recent_orders": recent_orders
    }

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
