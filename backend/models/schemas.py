"""
Pydantic models for Carter backend
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

# ==================== USER MODELS ====================

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    subscription_tier: str = "free_trial"
    trial_ends_at: Optional[datetime] = None
    subscription_ends_at: Optional[datetime] = None
    searches_today: int = 0
    purchased_searches: int = 0
    last_search_date: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionData(BaseModel):
    session_token: str
    user_id: str
    expires_at: datetime
    created_at: datetime

# ==================== MARKETPLACE MODELS ====================

class MarketplaceItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"item_{__import__('uuid').uuid4().hex[:12]}")
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

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    location: Optional[str] = None
    max_price: Optional[float] = None

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

class ProfitCalculation(BaseModel):
    purchase_price: float
    estimated_resale: float
    platform_fee: float
    shipping_cost: float
    net_profit: float
    profit_margin: float

# ==================== CHAT MODELS ====================

class MessageCreate(BaseModel):
    message: str

class Conversation(BaseModel):
    conversation_id: str = Field(default_factory=lambda: f"conv_{__import__('uuid').uuid4().hex[:12]}")
    participants: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_message: str = ""
    last_message_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    unread_count: dict = {}

class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{__import__('uuid').uuid4().hex[:12]}")
    conversation_id: str
    sender_id: str
    sender_name: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== DEAL ALERTS ====================

class DealAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alert_{__import__('uuid').uuid4().hex[:12]}")
    user_id: str
    category: str
    min_profit_margin: float = 20.0
    location: Optional[str] = None
    push_token: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== FEEDBACK MODELS ====================

class FeedbackCreate(BaseModel):
    category: str
    title: str
    description: str

class FeedbackResponse(BaseModel):
    feedback_id: str
    user_name: str
    category: str
    title: str
    description: str
    upvotes: int
    status: str
    created_at: datetime
    user_upvoted: bool = False
