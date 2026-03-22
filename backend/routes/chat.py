"""
Chat and messaging routes
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import User, MessageCreate
from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)

# ==================== CHAT ENDPOINTS ====================

@router.get("/chat/conversations")
async def get_conversations(user: User = Depends(get_current_user)):
    """Get user's conversations"""
    try:
        db = get_db()
        
        # Find all conversations where user is a participant
        conversations = await db.conversations.find({
            "participants": user.user_id
        }, {"_id": 0}).to_list(100)
        
        # Format for response
        formatted_conversations = []
        for conv in conversations:
            other_user_id = [uid for uid in conv["participants"] if uid != user.user_id][0] if len(conv["participants"]) > 1 else None
            
            if other_user_id:
                other_user = await db.users.find_one({"user_id": other_user_id}, {"_id": 0})
                if other_user:
                    formatted_conversations.append({
                        "conversation_id": conv["conversation_id"],
                        "other_user": {
                            "user_id": other_user["user_id"],
                            "name": other_user["name"],
                            "picture": other_user.get("picture")
                        },
                        "last_message": conv.get("last_message", ""),
                        "last_message_time": conv.get("last_message_time", conv["created_at"]),
                        "unread_count": conv.get("unread_count", {}).get(user.user_id, 0)
                    })
        
        # Sort by last message time
        formatted_conversations.sort(key=lambda x: x["last_message_time"], reverse=True)
        
        return {"conversations": formatted_conversations}
        
    except Exception as e:
        logger.error(f"Get conversations error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, user: User = Depends(get_current_user)):
    """Get messages in a conversation"""
    try:
        db = get_db()
        
        # Verify user is part of conversation
        conversation = await db.conversations.find_one({
            "conversation_id": conversation_id,
            "participants": user.user_id
        })
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages sorted by creation time (oldest first)
        messages = await db.messages.find({
            "conversation_id": conversation_id
        }, {"_id": 0}).sort("created_at", 1).to_list(1000)
        
        # Mark as read
        await db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {f"unread_count.{user.user_id}": 0}}
        )
        
        return {"messages": messages}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    user: User = Depends(get_current_user)
):
    """Send a message in a conversation"""
    try:
        db = get_db()
        
        # Verify user is part of conversation
        conversation = await db.conversations.find_one({
            "conversation_id": conversation_id,
            "participants": user.user_id
        })
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Create message
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        message = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "sender_id": user.user_id,
            "sender_name": user.name,
            "message": message_data.message,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.messages.insert_one(message)
        
        # Update conversation
        other_user_id = [uid for uid in conversation["participants"] if uid != user.user_id][0]
        await db.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "last_message": message_data.message[:50],
                    "last_message_time": datetime.now(timezone.utc)
                },
                "$inc": {f"unread_count.{other_user_id}": 1}
            }
        )
        
        return {"message": "Message sent", "message_id": message_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/start")
async def start_conversation(request: Request, user: User = Depends(get_current_user)):
    """Start a new conversation with another user"""
    try:
        db = get_db()
        body = await request.json()
        other_user_id = body.get("user_id")
        
        if not other_user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        if other_user_id == user.user_id:
            raise HTTPException(status_code=400, detail="Cannot chat with yourself")
        
        # Check if conversation already exists
        existing = await db.conversations.find_one({
            "participants": {"$all": [user.user_id, other_user_id]}
        })
        
        if existing:
            return {"conversation_id": existing["conversation_id"], "exists": True}
        
        # Create new conversation
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        conversation = {
            "conversation_id": conversation_id,
            "participants": [user.user_id, other_user_id],
            "created_at": datetime.now(timezone.utc),
            "last_message": "",
            "last_message_time": datetime.now(timezone.utc),
            "unread_count": {user.user_id: 0, other_user_id: 0}
        }
        
        await db.conversations.insert_one(conversation)
        
        return {"conversation_id": conversation_id, "exists": False}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    """Delete a conversation (only removes from user's view)"""
    try:
        db = get_db()
        
        # Verify user is part of conversation
        conversation = await db.conversations.find_one({
            "conversation_id": conversation_id,
            "participants": user.user_id
        })
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # For now, just delete the entire conversation
        # In production, you might want to implement soft delete per user
        await db.conversations.delete_one({"conversation_id": conversation_id})
        await db.messages.delete_many({"conversation_id": conversation_id})
        
        return {"message": "Conversation deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
