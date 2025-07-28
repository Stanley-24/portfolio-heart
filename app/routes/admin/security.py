from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.routes.auth import get_current_admin
from app.core.database import get_db
from app.core.security import audit_logger, rate_limiter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/audit-logs", summary="Get Audit Logs (Admin)")
def get_audit_logs(
    hours: int = Query(24, description="Number of hours to look back"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    admin_only: bool = Query(False, description="Show only admin actions"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get recent audit logs"""
    events = audit_logger.get_recent_events(hours=hours, event_type=event_type)
    
    if admin_only:
        events = [event for event in events if event.get("admin_action", False)]
    
    # Format events for display
    formatted_events = []
    for event in events:
        formatted_event = {
            "timestamp": event["timestamp"],
            "event_type": event["event_type"],
            "user_ip": event["user_ip"],
            "endpoint": event["endpoint"],
            "method": event["method"],
            "status_code": event["status_code"],
            "admin_action": event.get("admin_action", False),
            "user_agent": event.get("user_agent", "unknown")[:100],  # Truncate long user agents
            "request_data": event.get("request_data"),
            "response_data": event.get("response_data")
        }
        formatted_events.append(formatted_event)
    
    return {
        "events": formatted_events,
        "total_count": len(formatted_events),
        "time_range": f"Last {hours} hours"
    }

@router.get("/security-alerts", summary="Get Security Alerts (Admin)")
def get_security_alerts(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get security alerts"""
    alerts = audit_logger.get_security_alerts(hours=hours)
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "time_range": f"Last {hours} hours"
    }

@router.get("/rate-limit-stats", summary="Get Rate Limit Statistics (Admin)")
def get_rate_limit_stats(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get rate limit statistics"""
    # Get recent rate limit violations
    rate_limit_events = audit_logger.get_recent_events(
        hours=24, 
        event_type="rate_limit_exceeded"
    )
    
    # Group by endpoint
    endpoint_violations = {}
    for event in rate_limit_events:
        endpoint = event["endpoint"]
        if endpoint not in endpoint_violations:
            endpoint_violations[endpoint] = []
        endpoint_violations[endpoint].append(event)
    
    # Get current rate limit configurations
    rate_limit_configs = {}
    for endpoint, config in rate_limiter.limits.items():
        rate_limit_configs[endpoint] = {
            "max_requests": config["requests"],
            "window_seconds": config["window"],
            "window_minutes": config["window"] // 60
        }
    
    return {
        "rate_limit_violations": {
            endpoint: {
                "count": len(violations),
                "recent_violations": violations[:10]  # Show last 10 violations
            }
            for endpoint, violations in endpoint_violations.items()
        },
        "rate_limit_configs": rate_limit_configs,
        "total_violations_24h": len(rate_limit_events)
    }

@router.get("/activity-summary", summary="Get Activity Summary (Admin)")
def get_activity_summary(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get activity summary"""
    events = audit_logger.get_recent_events(hours=hours)
    
    # Count by event type
    event_counts = {}
    ip_activity = {}
    status_codes = {}
    admin_actions = 0
    errors = 0
    
    for event in events:
        # Event type counts
        event_type = event["event_type"]
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # IP activity
        ip = event["user_ip"]
        if ip not in ip_activity:
            ip_activity[ip] = 0
        ip_activity[ip] += 1
        
        # Status code counts
        status_code = event["status_code"]
        status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        # Admin actions
        if event.get("admin_action", False):
            admin_actions += 1
        
        # Errors
        if status_code >= 400:
            errors += 1
    
    # Get top IPs by activity
    top_ips = sorted(ip_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Get top status codes
    top_status_codes = sorted(status_codes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "summary": {
            "total_requests": len(events),
            "admin_actions": admin_actions,
            "errors": errors,
            "unique_ips": len(ip_activity),
            "time_range": f"Last {hours} hours"
        },
        "event_type_counts": event_counts,
        "top_ips": [{"ip": ip, "count": count} for ip, count in top_ips],
        "top_status_codes": [{"code": code, "count": count} for code, count in top_status_codes],
        "admin_actions_percentage": (admin_actions / len(events) * 100) if events else 0,
        "error_rate": (errors / len(events) * 100) if events else 0
    }

@router.get("/suspicious-activity", summary="Get Suspicious Activity (Admin)")
def get_suspicious_activity(
    hours: int = Query(24, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Get suspicious activity patterns"""
    events = audit_logger.get_recent_events(hours=hours)
    
    suspicious_activities = []
    
    # Group by IP
    ip_events = {}
    for event in events:
        ip = event["user_ip"]
        if ip not in ip_events:
            ip_events[ip] = []
        ip_events[ip].append(event)
    
    # Analyze each IP for suspicious patterns
    for ip, ip_event_list in ip_events.items():
        if len(ip_event_list) > 50:  # High activity
            suspicious_activities.append({
                "type": "high_activity",
                "ip": ip,
                "count": len(ip_event_list),
                "description": f"High activity detected: {len(ip_event_list)} requests",
                "events": ip_event_list[:5]  # Show first 5 events
            })
        
        # Check for failed login attempts
        failed_logins = [e for e in ip_event_list 
                        if e["event_type"] == "admin_login" and e["status_code"] == 401]
        if len(failed_logins) > 5:
            suspicious_activities.append({
                "type": "failed_logins",
                "ip": ip,
                "count": len(failed_logins),
                "description": f"Multiple failed login attempts: {len(failed_logins)}",
                "events": failed_logins
            })
        
        # Check for rate limit violations
        rate_limit_violations = [e for e in ip_event_list 
                               if e["event_type"] == "rate_limit_exceeded"]
        if rate_limit_violations:
            suspicious_activities.append({
                "type": "rate_limit_violations",
                "ip": ip,
                "count": len(rate_limit_violations),
                "description": f"Rate limit violations: {len(rate_limit_violations)}",
                "events": rate_limit_violations
            })
        
        # Check for unusual user agents
        user_agents = set(e.get("user_agent", "") for e in ip_event_list)
        if len(user_agents) > 3:  # Multiple user agents from same IP
            suspicious_activities.append({
                "type": "multiple_user_agents",
                "ip": ip,
                "count": len(user_agents),
                "description": f"Multiple user agents from same IP: {len(user_agents)}",
                "user_agents": list(user_agents)[:5]  # Show first 5
            })
    
    return {
        "suspicious_activities": suspicious_activities,
        "total_suspicious": len(suspicious_activities),
        "time_range": f"Last {hours} hours"
    } 