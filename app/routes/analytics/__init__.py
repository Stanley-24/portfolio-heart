from fastapi import APIRouter, Depends, Request, Query
from typing import Optional
from app.routes.auth import get_current_admin
from app.core.analytics import analytics_tracker
from app.core.security import rate_limiter
from sqlalchemy.orm import Session
from app.core.database import get_db
import time

router = APIRouter()

@router.post("/track/page-view", summary="Track Page View")
def track_page_view(
    page: str = Query(..., description="Page path to track"),
    request: Request = None,
    referrer: Optional[str] = Query(None, description="Referrer URL"),
    session_id: Optional[str] = Query(None, description="Session ID")
):
    """Track a page view with analytics"""
    # Skip tracking admin routes
    if page.startswith("/admin"):
        return {"message": "Admin route skipped", "success": True}
    
    user_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    
    analytics_tracker.track_page_view(
        page=page,
        user_ip=user_ip,
        user_agent=user_agent,
        referrer=referrer,
        session_id=session_id
    )
    
    return {"message": "Page view tracked", "success": True}

@router.post("/track/conversion", summary="Track Conversion")
def track_conversion(
    conversion_type: str = Query(..., description="Type of conversion"),
    request: Request = None,
    session_id: Optional[str] = Query(None, description="Session ID"),
    metadata: Optional[str] = Query(None, description="JSON string of metadata")
):
    """Track a conversion event"""
    user_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Parse metadata if provided
    parsed_metadata = None
    if metadata:
        try:
            import json
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            parsed_metadata = {"raw_metadata": metadata}
    
    analytics_tracker.track_conversion(
        conversion_type=conversion_type,
        user_ip=user_ip,
        user_agent=user_agent,
        session_id=session_id,
        metadata=parsed_metadata
    )
    
    return {"message": "Conversion tracked", "success": True}

@router.post("/track/behavior", summary="Track User Behavior")
def track_user_behavior(
    action: str = Query(..., description="Action type"),
    request: Request = None,
    session_id: Optional[str] = Query(None, description="Session ID"),
    data: Optional[str] = Query(None, description="JSON string of additional data")
):
    """Track user behavior event"""
    # Skip tracking admin-related behavior
    if action.startswith("admin_") or "admin" in action.lower():
        return {"message": "Admin behavior skipped", "success": True}
    
    user_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    
    # Parse data if provided
    parsed_data = None
    if data:
        try:
            import json
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            parsed_data = {"raw_data": data}
    
    analytics_tracker.track_user_behavior(
        action=action,
        user_ip=user_ip,
        user_agent=user_agent,
        session_id=session_id,
        data=parsed_data
    )
    
    return {"message": "Behavior tracked", "success": True}

@router.get("/summary", summary="Get Analytics Summary (Admin)")
def get_analytics_summary(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get comprehensive analytics summary"""
    summary = analytics_tracker.get_analytics_summary(hours=hours)
    return summary

@router.get("/geographic", summary="Get Geographic Analytics (Admin)")
def get_geographic_analytics(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get geographic analytics data"""
    geo_data = analytics_tracker.get_geographic_analytics(hours=hours)
    return geo_data

@router.get("/performance", summary="Get Performance Analytics (Admin)")
def get_performance_analytics(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get performance analytics data"""
    performance_data = analytics_tracker.get_performance_analytics(hours=hours)
    return performance_data

@router.get("/user-behavior", summary="Get User Behavior Analytics (Admin)")
def get_user_behavior_analytics(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get user behavior analytics data"""
    behavior_data = analytics_tracker.get_user_behavior_analytics(hours=hours)
    return behavior_data

@router.get("/conversions", summary="Get Conversion Analytics (Admin)")
def get_conversion_analytics(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get conversion analytics data"""
    summary = analytics_tracker.get_analytics_summary(hours=hours)
    
    return {
        "time_period": summary["time_period"],
        "total_conversions": summary["total_conversions"],
        "conversion_rate": summary["conversion_rate"],
        "conversions_by_type": summary["conversions"],
        "top_conversions": summary["top_conversions"],
        "geographic_conversions": {
            location: data["conversions"] 
            for location, data in summary["geographic_data"].items()
            if data.get("conversions")
        }
    }

@router.get("/real-time", summary="Get Real-time Analytics (Admin)")
def get_real_time_analytics(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get real-time analytics data (last hour)"""
    real_time_data = analytics_tracker.get_analytics_summary(hours=1)
    
    # Add real-time specific metrics
    real_time_data["real_time"] = {
        "active_sessions": len([
            s for s in analytics_tracker.user_sessions.values()
            if (time.time() - s["start_time"].timestamp()) < 3600  # Last hour
        ]),
        "current_minute_requests": len([
            e for e in analytics_tracker.events
            if (time.time() - time.mktime(time.strptime(e["timestamp"], "%Y-%m-%dT%H:%M:%S.%f"))) < 60
        ])
    }
    
    return real_time_data

@router.get("/trends", summary="Get Analytics Trends (Admin)")
def get_analytics_trends(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get analytics trends over time"""
    trends = {
        "daily_page_views": [],
        "daily_conversions": [],
        "daily_conversion_rates": [],
        "daily_performance": []
    }
    
    for day in range(days):
        day_data = analytics_tracker.get_analytics_summary(hours=24)
        
        trends["daily_page_views"].append({
            "day": day,
            "page_views": day_data["total_page_views"]
        })
        
        trends["daily_conversions"].append({
            "day": day,
            "conversions": day_data["total_conversions"]
        })
        
        trends["daily_conversion_rates"].append({
            "day": day,
            "conversion_rate": day_data["conversion_rate"]
        })
        
        trends["daily_performance"].append({
            "day": day,
            "avg_response_time": day_data["performance"]["avg_response_time"]
        })
    
    return trends 