from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
import uuid
from app.routes.auth import get_current_admin

router = APIRouter()

# Fake in-memory DB
fake_review_db = []

# Helper: validate review fields
def validate_review(data: ReviewCreate):
    if not data.name or not data.review or not data.rating:
        raise HTTPException(status_code=400, detail="Name, review, and rating are required.")
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

@router.get("/", response_model=List[Review], summary="List Reviews")
def list_reviews():
    """List all reviews."""
    return fake_review_db

@router.post("/", summary="Add Review")
def create_review(data: ReviewCreate):
    try:
        validate_review(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    new_id = str(uuid.uuid4())
    new_review = Review(id=new_id, **data.model_dump())
    fake_review_db.append(new_review)
    return {"message": "Review created successfully.", "success": True, "review": new_review}

@router.put("/{review_id}", summary="Update Review")
def update_review(review_id: str, data: ReviewUpdate, admin=Depends(get_current_admin)):
    try:
        validate_review(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    for i, old_review in enumerate(fake_review_db):
        if old_review.id == review_id:
            updated_review = Review(id=review_id, **data.model_dump())
            fake_review_db[i] = updated_review
            return {"message": "Review updated successfully.", "success": True, "review": updated_review}
    return {"message": "Review not found", "success": False}

@router.delete("/{review_id}", status_code=200, summary="Delete Review")
def delete_review(review_id: str, admin=Depends(get_current_admin)):
    for i, review in enumerate(fake_review_db):
        if review.id == review_id:
            del fake_review_db[i]
            return {"message": "Review deleted successfully.", "success": True}
    return {"message": "Review not found", "success": False} 