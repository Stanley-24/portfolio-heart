from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.review import Review as ReviewSchema, ReviewCreate, ReviewUpdate
from app.models.review import Review
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.routes.auth import get_current_admin

router = APIRouter()

# Helper: validate review fields
def validate_review(data: ReviewCreate):
    if not data.client_name or not data.review_text or not data.rating:
        raise HTTPException(status_code=400, detail="Name, review, and rating are required.")
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

@router.get("/", response_model=List[ReviewSchema], summary="List Reviews")
def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()

@router.post("/", summary="Add Review")
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    try:
        validate_review(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    new_review = Review(**data.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return {"message": "Review created successfully.", "success": True, "review": new_review}

@router.put("/{review_id}", summary="Update Review")
def update_review(review_id: int, data: ReviewUpdate, db: Session = Depends(get_db)):
    try:
        validate_review(data)
    except HTTPException as e:
        return {"message": str(e.detail), "success": False}
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return {"message": "Review not found", "success": False}
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return {"message": "Review updated successfully.", "success": True, "review": review}

@router.delete("/{review_id}", status_code=200, summary="Delete Review")
def delete_review(review_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return {"message": "Review not found", "success": False}
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully.", "success": True} 