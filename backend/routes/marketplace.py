"""
Marketplace search and listings routes
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid
import os
import logging
import requests
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import (
    User, MarketplaceItem, SavedItem, SearchRequest,
    PriceEstimateRequest, PriceEstimateResponse, ProfitCalculation
)
from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter(tags=["Marketplace"])
logger = logging.getLogger(__name__)

# Environment variables
EMERGENT_LLM_KEY = os.getenv('EMERGENT_LLM_KEY', '')
SERPAPI_KEY = os.getenv('SERPAPI_API_KEY', '')

# ==================== HELPER FUNCTIONS ====================

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

async def estimate_resale_price_with_ai(title: str, category: str = ""):
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

# ==================== MARKETPLACE ENDPOINTS ====================

@router.post("/search")
async def search_marketplace(search_req: SearchRequest, user: User = Depends(get_current_user)):
    """Search marketplaces using SerpApi"""
    try:
        db = get_db()
        
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

@router.post("/estimate-price", response_model=PriceEstimateResponse)
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

@router.post("/saved-items")
async def save_item(item: MarketplaceItem, user: User = Depends(get_current_user)):
    """Save an item"""
    try:
        db = get_db()
        
        saved = SavedItem(
            user_id=user.user_id,
            item=item
        )
        
        await db.saved_items.insert_one(saved.dict())
        return {"message": "Item saved", "item_id": item.item_id}
        
    except Exception as e:
        logger.error(f"Save item error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved-items")
async def get_saved_items(user: User = Depends(get_current_user)):
    """Get user's saved items"""
    try:
        db = get_db()
        
        items = await db.saved_items.find(
            {"user_id": user.user_id},
            {"_id": 0}
        ).sort("saved_at", -1).to_list(100)
        
        return {"items": items}
        
    except Exception as e:
        logger.error(f"Get saved items error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/saved-items/{item_id}")
async def delete_saved_item(item_id: str, user: User = Depends(get_current_user)):
    """Delete a saved item"""
    try:
        db = get_db()
        
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
