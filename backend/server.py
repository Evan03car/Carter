from fastapi import FastAPI, APIRouter, HTTPException, Cookie, Request, Header, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import requests
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse
import base64
import json
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment variables
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
EMERGENT_LLM_KEY = os.getenv('EMERGENT_LLM_KEY', 'sk-emergent-dD63aC815B86318A93')
SERPAPI_KEY = os.getenv('SERPAPI_API_KEY', '')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', 'sk_test_emergent')

# MongoDB connection
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    subscription_tier: str = "free_trial"  # free_trial, basic, premium
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    searches_today: int = 0
    purchased_searches: int = 0  # Additional searches purchased
    last_search_date: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionData(BaseModel):
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime

class MarketplaceItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"item_{uuid.uuid4().hex[:12]}")
    title: str
    price: float
    estimated_resale_price: Optional[float] = None
    profit_margin: Optional[float] = None
    platform: str
    url: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    demand_level: Optional[str] = None
    best_resell_platform: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SavedItem(BaseModel):
    user_id: str
    item: MarketplaceItem
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DealAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alert_{uuid.uuid4().hex[:12]}")
    user_id: Optional[str] = None
    category: str
    min_profit_margin: float = 20.0
    location: Optional[str] = None
    push_token: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PriceEstimateRequest(BaseModel):
    listing_url: Optional[str] = None
    image_base64: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class PriceEstimateResponse(BaseModel):
    estimated_price: float
    confidence: str
    demand_level: str
    best_platform: str
    analysis: str

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    location: Optional[str] = None
    max_price: Optional[float] = None

class ProfitCalculation(BaseModel):
    purchase_price: float
    estimated_resale: float
    platform_fee: float
    shipping_cost: float
    net_profit: float
    profit_margin: float

# ==================== AUTHENTICATION ====================

async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    """Get current user from session token (cookie or header)"""
    token = session_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

@api_router.post("/auth/session")
async def create_session(request: Request):
    """Exchange session_id for session_token"""
    try:
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session_id")
        
        # Call Emergent Auth API
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get session data")
        
        data = response.json()
        email = data["email"]
        name = data["name"]
        picture = data.get("picture")
        session_token = data["session_token"]
        
        # Check if user exists
        user = await db.users.find_one({"email": email}, {"_id": 0})
        
        if not user:
            # Create new user with 7-day trial
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            trial_ends = datetime.now(timezone.utc) + timedelta(days=7)
            user_data = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "subscription_tier": "free_trial",
                "trial_ends_at": trial_ends,
                "searches_today": 0,
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(user_data)
            user = user_data
        else:
            user_id = user["user_id"]
        
        # Store session
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        session_data = {
            "session_token": session_token,
            "user_id": user_id,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        await db.user_sessions.insert_one(session_data)
        
        # Return user data
        response = JSONResponse(content={
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "subscription_tier": user.get("subscription_tier", "free_trial")
        })
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7*24*60*60,
            path="/"
        )
        return response
        
    except Exception as e:
        logger.error(f"Session creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return user

@api_router.post("/auth/logout")
async def logout(session_token: Optional[str] = Cookie(None)):
    """Logout user"""
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_token", path="/")
    return response

# ==================== MARKETPLACE SEARCH ====================

def calculate_profit(purchase_price: float, estimated_resale: float, platform: str = "ebay") -> ProfitCalculation:
    """Calculate profit with fees and shipping"""
    # Platform fees (approximate)
    fee_rates = {
        "ebay": 0.13,  # 13%
        "mercari": 0.125,  # 12.5%
        "poshmark": 0.20,  # 20%
        "facebook": 0.05,  # 5%
        "other": 0.10  # 10%
    }
    
    fee_rate = fee_rates.get(platform.lower(), 0.10)
    platform_fee = estimated_resale * fee_rate
    shipping_cost = min(10.0, estimated_resale * 0.08)  # Estimate 8% or $10 max
    
    net_profit = estimated_resale - purchase_price - platform_fee - shipping_cost
    profit_margin = (net_profit / purchase_price * 100) if purchase_price > 0 else 0
    
    return ProfitCalculation(
        purchase_price=purchase_price,
        estimated_resale=estimated_resale,
        platform_fee=platform_fee,
        shipping_cost=shipping_cost,
        net_profit=net_profit,
        profit_margin=profit_margin
    )

async def estimate_resale_price_with_ai(title: str, category: str = "") -> Dict[str, Any]:
    """Use Gemini AI to estimate resale price"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"price_estimate_{uuid.uuid4().hex[:8]}",
            system_message="You are a resale expert. Analyze items and provide realistic resale price estimates based on current market trends."
        ).with_model("gemini", "gemini-2.5-flash")
        
        prompt = f"""Analyze this item for resale potential:

Title: {title}
Category: {category or 'General'}

Provide a JSON response with:
{{
  "estimated_price": <number>,
  "confidence": "high|medium|low",
  "demand_level": "high|medium|low",
  "best_platform": "ebay|mercari|poshmark|facebook",
  "analysis": "<brief analysis>"
}}

Be realistic and consider current market conditions."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse JSON from response
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        logger.error(f"AI estimation error: {str(e)}")
        # Fallback to basic estimation
        return {
            "estimated_price": 0,
            "confidence": "low",
            "demand_level": "medium",
            "best_platform": "ebay",
            "analysis": "Could not estimate price accurately"
        }

@api_router.post("/search")
async def search_marketplace(search_req: SearchRequest, user: User = Depends(get_current_user)):
    """Search marketplaces using SerpApi"""
    try:
        
        # Check subscription limits
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if user.last_search_date != today:
            await db.users.update_one(
                {"user_id": user.user_id},
                {"$set": {"searches_today": 0, "last_search_date": today}}
            )
            user.searches_today = 0
        
        # Free trial: 10 searches/day, Basic: 10/day, Premium: 300/day
        limits = {"free_trial": 10, "basic": 10, "premium": 300}
        limit = limits.get(user.subscription_tier, 10)
        
        # Check if user has purchased searches
        purchased_searches = user.dict().get("purchased_searches", 0)
        
        if user.searches_today >= limit and purchased_searches <= 0:
            raise HTTPException(
                status_code=429, 
                detail=f"Daily search limit reached. Upgrade your plan or purchase additional searches!"
            )
        
        # Search using SerpApi (eBay for now)
        params = {
            "engine": "ebay",
            "ebay_domain": "ebay.com",
            "_nkw": search_req.query,
            "api_key": SERPAPI_KEY
        }
        
        if search_req.max_price:
            params["_udhi"] = search_req.max_price
        
        response = requests.get("https://serpapi.com/search", params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Marketplace search failed")
        
        data = response.json()
        organic_results = data.get("organic_results", [])
        
        items = []
        for result in organic_results[:20]:  # Limit to 20 results
            try:
                title = result.get("title", "")
                price_str = result.get("price", {}).get("raw", "$0")
                price = float(price_str.replace("$", "").replace(",", ""))
                
                # Get AI estimate
                ai_estimate = await estimate_resale_price_with_ai(title, search_req.category or "")
                estimated_price = ai_estimate.get("estimated_price", price * 1.5)
                
                # Calculate profit
                profit_calc = calculate_profit(price, estimated_price, "ebay")
                
                # Only include if profitable
                if profit_calc.profit_margin >= 15:  # 15% minimum margin
                    item = MarketplaceItem(
                        title=title,
                        price=price,
                        estimated_resale_price=estimated_price,
                        profit_margin=profit_calc.profit_margin,
                        platform="eBay",
                        url=result.get("link"),
                        image_url=result.get("thumbnail"),
                        location=result.get("location"),
                        category=search_req.category,
                        demand_level=ai_estimate.get("demand_level"),
                        best_resell_platform=ai_estimate.get("best_platform")
                    )
                    items.append(item.dict())
            except Exception as e:
                logger.error(f"Error processing result: {str(e)}")
                continue
        
        # Update search count
        update_data = {"$inc": {"searches_today": 1}}
        
        # Deduct from purchased searches if available
        if user.dict().get("purchased_searches", 0) > 0:
            update_data["$inc"]["purchased_searches"] = -1
        
        await db.users.update_one(
            {"user_id": user.user_id},
            update_data
        )
        
        # Sort by profit margin
        items.sort(key=lambda x: x.get("profit_margin", 0), reverse=True)
        
        return {
            "items": items[:15],  # Return top 15
            "searches_remaining": max(0, limit - user.searches_today - 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PRICE ESTIMATOR ====================

@api_router.post("/estimate-price", response_model=PriceEstimateResponse)
async def estimate_price(request: PriceEstimateRequest, user: User = Depends(get_current_user)):
    """AI-powered price estimation from URL or image"""
    try:
        
        prompt = "Analyze this item for resale value. Provide estimated price, demand level, and best platform to sell."
        
        if request.listing_url:
            prompt += f"\n\nListing URL: {request.listing_url}"
        
        if request.title:
            prompt += f"\n\nTitle: {request.title}"
        
        if request.description:
            prompt += f"\n\nDescription: {request.description}"
        
        prompt += "\n\nProvide response as JSON with: estimated_price (number), confidence (high/medium/low), demand_level (high/medium/low), best_platform (ebay/mercari/poshmark/facebook), analysis (string)."
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"estimate_{uuid.uuid4().hex[:8]}",
            system_message="You are an expert reseller with deep knowledge of online marketplace prices and trends."
        ).with_model("gemini", "gemini-2.5-pro")
        
        # Add image if provided
        file_contents = []
        if request.image_base64:
            image_content = ImageContent(image_base64=request.image_base64)
            file_contents.append(image_content)
        
        response = await chat.send_message(
            UserMessage(text=prompt, file_contents=file_contents if file_contents else None)
        )
        
        # Parse response
        response_text = response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response_text)
        
        return PriceEstimateResponse(
            estimated_price=data.get("estimated_price", 0),
            confidence=data.get("confidence", "low"),
            demand_level=data.get("demand_level", "medium"),
            best_platform=data.get("best_platform", "ebay"),
            analysis=data.get("analysis", "Analysis completed")
        )
        
    except Exception as e:
        logger.error(f"Price estimation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SAVED ITEMS ====================

@api_router.post("/saved-items")
async def save_item(item: MarketplaceItem, user: User = Depends(get_current_user)):
    """Save an item"""
    try:
        
        saved = SavedItem(
            user_id=user.user_id,
            item=item
        )
        
        await db.saved_items.insert_one(saved.dict())
        return {"message": "Item saved", "item_id": item.item_id}
        
    except Exception as e:
        logger.error(f"Save item error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/saved-items")
async def get_saved_items(user: User = Depends(get_current_user)):
    """Get user's saved items"""
    try:
        
        items = await db.saved_items.find(
            {"user_id": user.user_id},
            {"_id": 0}
        ).sort("saved_at", -1).to_list(100)
        
        return {"items": items}
        
    except Exception as e:
        logger.error(f"Get saved items error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/saved-items/{item_id}")
async def delete_saved_item(item_id: str, user: User = Depends(get_current_user)):
    """Delete a saved item"""
    try:
        
        result = await db.saved_items.delete_one({
            "user_id": user.user_id,
            "item.item_id": item_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"message": "Item deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete saved item error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DEAL ALERTS ====================

@api_router.post("/deal-alerts")
async def create_deal_alert(alert: DealAlert, user: User = Depends(get_current_user)):
    """Create a deal alert"""
    try:
        alert.user_id = user.user_id
        
        await db.deal_alerts.insert_one(alert.dict())
        return {"message": "Alert created", "alert_id": alert.alert_id}
        
    except Exception as e:
        logger.error(f"Create alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/deal-alerts")
async def get_deal_alerts(user: User = Depends(get_current_user)):
    """Get user's deal alerts"""
    try:
        
        alerts = await db.deal_alerts.find(
            {"user_id": user.user_id},
            {"_id": 0}
        ).to_list(100)
        
        return {"alerts": alerts}
        
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/deal-alerts/{alert_id}")
async def delete_deal_alert(alert_id: str, user: User = Depends(get_current_user)):
    """Delete a deal alert"""
    try:
        
        result = await db.deal_alerts.delete_one({
            "user_id": user.user_id,
            "alert_id": alert_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SUBSCRIPTIONS ====================

@api_router.post("/subscriptions/checkout")
async def create_subscription_checkout(request: Request, user: User = Depends(get_current_user)):
    """Create Stripe checkout for subscription or search pack"""
    try:
        body = await request.json()
        
        product_type = body.get("type", "subscription")  # subscription or search_pack
        origin_url = body.get("origin_url", "")
        
        if not origin_url:
            raise HTTPException(status_code=400, detail="Missing origin_url")
        
        # Fixed pricing
        if product_type == "subscription":
            plan = body.get("plan", "basic")  # basic or premium
            prices = {"basic": 12.0, "premium": 40.0}
            amount = prices.get(plan, 12.0)
            metadata = {
                "user_id": user.user_id,
                "plan": plan,
                "type": "subscription"
            }
        elif product_type == "search_pack":
            pack = body.get("pack", "10")  # 10 or 25
            prices = {"10": 5.0, "25": 7.0}
            amount = prices.get(pack, 5.0)
            metadata = {
                "user_id": user.user_id,
                "searches": pack,
                "type": "search_pack"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid product type")
        
        host_url = origin_url
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        success_url = f"{origin_url}/profile?session_id={{{{CHECKOUT_SESSION_ID}}}}"
        cancel_url = f"{origin_url}/profile"
        
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store pending transaction
        await db.payment_transactions.insert_one({
            "session_id": session.session_id,
            "user_id": user.user_id,
            "amount": amount,
            "product_type": product_type,
            "metadata": metadata,
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc)
        })
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/subscriptions/status/{session_id}")
async def check_payment_status(session_id: str, user: User = Depends(get_current_user)):
    """Check payment status"""
    try:
        
        host_url = "https://example.com"  # Not used for status check
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction if paid
        if status.payment_status == "paid":
            transaction = await db.payment_transactions.find_one({"session_id": session_id})
            
            if transaction and transaction.get("payment_status") != "completed":
                product_type = transaction.get("product_type", "subscription")
                metadata = transaction.get("metadata", {})
                
                if product_type == "subscription":
                    plan = metadata.get("plan", "basic")
                    # Update user subscription
                    subscription_ends = datetime.now(timezone.utc) + timedelta(days=30)
                    await db.users.update_one(
                        {"user_id": user.user_id},
                        {
                            "$set": {
                                "subscription_tier": plan,
                                "subscription_ends_at": subscription_ends
                            }
                        }
                    )
                elif product_type == "search_pack":
                    searches = int(metadata.get("searches", "10"))
                    # Add purchased searches
                    await db.users.update_one(
                        {"user_id": user.user_id},
                        {"$inc": {"purchased_searches": searches}}
                    )
                
                # Mark transaction as completed
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"payment_status": "completed", "completed_at": datetime.now(timezone.utc)}}
                )
        
        return status.dict()
        
    except Exception as e:
        logger.error(f"Payment status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        webhook_url = "https://example.com/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Webhook received: {webhook_response.event_type}")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

# ==================== DASHBOARD ====================

@api_router.get("/")
async def root():
    """API root"""
    return {"message": "Carter API", "version": "1.0"}

@api_router.get("/dashboard")
async def get_dashboard(user: User = Depends(get_current_user)):
    """Get dashboard data"""
    try:
        
        # Get saved items count
        saved_count = await db.saved_items.count_documents({"user_id": user.user_id})
        
        # Get active alerts
        alerts_count = await db.deal_alerts.count_documents({
            "user_id": user.user_id,
            "active": True
        })
        
        # Check subscription status
        subscription_status = "active"
        days_remaining = 0
        
        if user.subscription_tier == "free_trial" and user.trial_ends_at:
            trial_end = user.trial_ends_at
            if isinstance(trial_end, str):
                trial_end = datetime.fromisoformat(trial_end)
            if trial_end.tzinfo is None:
                trial_end = trial_end.replace(tzinfo=timezone.utc)
            
            days_remaining = max(0, (trial_end - datetime.now(timezone.utc)).days)
            if days_remaining == 0:
                subscription_status = "trial_ended"
        
        elif user.subscription_tier in ["basic", "premium"] and user.subscription_ends_at:
            sub_end = user.subscription_ends_at
            if isinstance(sub_end, str):
                sub_end = datetime.fromisoformat(sub_end)
            if sub_end.tzinfo is None:
                sub_end = sub_end.replace(tzinfo=timezone.utc)
            
            days_remaining = max(0, (sub_end - datetime.now(timezone.utc)).days)
            if days_remaining == 0:
                subscription_status = "expired"
        
        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "subscription_tier": user.subscription_tier,
                "subscription_status": subscription_status,
                "days_remaining": days_remaining,
                "purchased_searches": user.dict().get("purchased_searches", 0)
            },
            "stats": {
                "saved_items": saved_count,
                "active_alerts": alerts_count,
                "searches_today": user.searches_today
            }
        }
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
