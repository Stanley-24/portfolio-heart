from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.newsletter import Newsletter, NewsletterCreate, NewsletterUpdate
import uuid
from datetime import datetime
from app.routes.auth import get_current_admin

router = APIRouter()

# Fake in-memory DB
fake_newsletter_db = []

# Helper: validate newsletter fields
def validate_newsletter(data: NewsletterCreate):
    if not data.email:
        raise HTTPException(status_code=400, detail="Email is required.")

@router.get("/", response_model=List[Newsletter], summary="List Subscribers")
def list_subscribers(admin=Depends(get_current_admin)):
    """List all newsletter subscribers."""
    return fake_newsletter_db

@router.post("/subscribe", summary="Subscribe to Newsletter")
def subscribe_newsletter(data: NewsletterCreate):
    try:
        validate_newsletter(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    # Prevent duplicate emails
    for sub in fake_newsletter_db:
        if sub.email == data.email:
            return {"message": "Email already subscribed.", "success": False}
    new_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    payload = {**data.model_dump(), "subscribed_at": now}
    new_sub = Newsletter(id=new_id, **payload)
    fake_newsletter_db.append(new_sub)
    return {"message": "Subscribed successfully.", "success": True, "subscriber": new_sub}

@router.put("/{subscriber_id}", summary="Update Subscriber")
def update_subscriber(subscriber_id: str, data: NewsletterUpdate, admin=Depends(get_current_admin)):
    try:
        validate_newsletter(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    for i, sub in enumerate(fake_newsletter_db):
        if sub.id == subscriber_id:
            payload = {**data.model_dump(), "subscribed_at": sub.subscribed_at}
            updated_sub = Newsletter(id=subscriber_id, **payload)
            fake_newsletter_db[i] = updated_sub
            return {"message": "Subscriber updated successfully.", "success": True, "subscriber": updated_sub}
    return {"message": "Subscriber not found", "success": False}

@router.delete("/{subscriber_id}", status_code=200, summary="Delete Subscriber")
def delete_subscriber(subscriber_id: str, admin=Depends(get_current_admin)):
    for i, sub in enumerate(fake_newsletter_db):
        if sub.id == subscriber_id:
            del fake_newsletter_db[i]
            return {"message": "Subscriber deleted successfully.", "success": True}
    return {"message": "Subscriber not found", "success": False}

@router.post("/unsubscribe/{subscriber_id}", summary="Unsubscribe from Newsletter")
def unsubscribe_newsletter(subscriber_id: str):
    for i, sub in enumerate(fake_newsletter_db):
        if sub.id == subscriber_id:
            if not sub.is_active:
                return {"message": "Subscriber is already unsubscribed.", "success": False}
            unsub_time = datetime.utcnow().isoformat()
            updated_sub = Newsletter(
                id=sub.id,
                email=sub.email,
                is_active=False,
                subscribed_at=sub.subscribed_at,
                unsubscribed_at=unsub_time
            )
            fake_newsletter_db[i] = updated_sub
            return {"message": "Unsubscribed successfully.", "success": True, "subscriber": updated_sub}
    return {"message": "Subscriber not found", "success": False} 