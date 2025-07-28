import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Request
from collections import defaultdict
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.limits = {
            # Contact endpoints
            "contact_send_message": {"requests": 5, "window": 300},  # 5 requests per 5 minutes
            "contact_book_call": {"requests": 3, "window": 300},     # 3 requests per 5 minutes
            
            # Review endpoints
            "review_create": {"requests": 2, "window": 3600},        # 2 reviews per hour
            
            # Newsletter endpoints
            "newsletter_subscribe": {"requests": 3, "window": 3600}, # 3 subscriptions per hour
            
            # Resume endpoints
            "resume_download": {"requests": 10, "window": 3600},     # 10 downloads per hour
            
            # Admin endpoints
            "admin_login": {"requests": 5, "window": 300},           # 5 login attempts per 5 minutes
            "admin_change_password": {"requests": 3, "window": 3600}, # 3 password changes per hour
            
            # General API
            "api_general": {"requests": 100, "window": 3600},        # 100 requests per hour
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (for proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _get_user_agent(self, request: Request) -> str:
        """Get user agent for additional identification"""
        return request.headers.get("User-Agent", "unknown")
    
    def _generate_key(self, request: Request, endpoint: str) -> str:
        """Generate unique key for rate limiting"""
        client_ip = self._get_client_ip(request)
        user_agent = self._get_user_agent(request)
        
        # Create a hash of IP + User-Agent + Endpoint
        key_data = f"{client_ip}:{user_agent}:{endpoint}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def is_rate_limited(self, request: Request, endpoint: str) -> bool:
        """Check if request should be rate limited"""
        key = self._generate_key(request, endpoint)
        now = time.time()
        
        # Get rate limit config
        limit_config = self.limits.get(endpoint, self.limits["api_general"])
        max_requests = limit_config["requests"]
        window = limit_config["window"]
        
        # Clean old requests outside the window
        self.requests[key] = [req_time for req_time in self.requests[key] 
                            if now - req_time < window]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            return True
        
        # Add current request
        self.requests[key].append(now)
        return False
    
    def get_remaining_requests(self, request: Request, endpoint: str) -> Dict[str, Any]:
        """Get remaining requests and reset time"""
        key = self._generate_key(request, endpoint)
        now = time.time()
        
        limit_config = self.limits.get(endpoint, self.limits["api_general"])
        max_requests = limit_config["requests"]
        window = limit_config["window"]
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] 
                            if now - req_time < window]
        
        remaining = max(0, max_requests - len(self.requests[key]))
        
        # Calculate reset time
        if self.requests[key]:
            oldest_request = min(self.requests[key])
            reset_time = oldest_request + window
        else:
            reset_time = now
        
        return {
            "remaining": remaining,
            "limit": max_requests,
            "reset_time": reset_time,
            "window": window
        }

class AuditLogger:
    """Audit logger for security events"""
    
    def __init__(self):
        self.log_file = "audit.log"
        self.sensitive_fields = {"password", "token", "secret", "key"}
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove sensitive data from logs"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def log_event(self, event_type: str, user_ip: str, user_agent: str, 
                  endpoint: str, method: str, status_code: int, 
                  request_data: Optional[Dict] = None, 
                  response_data: Optional[Dict] = None,
                  user_id: Optional[str] = None,
                  admin_action: bool = False):
        """Log security event"""
        timestamp = datetime.utcnow().isoformat()
        
        # Sanitize sensitive data
        sanitized_request = self._sanitize_data(request_data) if request_data else None
        sanitized_response = self._sanitize_data(response_data) if response_data else None
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_ip": user_ip,
            "user_agent": user_agent,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "user_id": user_id,
            "admin_action": admin_action,
            "request_data": sanitized_request,
            "response_data": sanitized_response
        }
        
        # Write to log file
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
        
        # Also log to console for important events
        if admin_action or status_code >= 400:
            logger.info(f"AUDIT: {event_type} - {method} {endpoint} - Status: {status_code} - IP: {user_ip}")
    
    def get_recent_events(self, hours: int = 24, event_type: Optional[str] = None) -> List[Dict]:
        """Get recent audit events"""
        events = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event["timestamp"])
                        
                        if event_time >= cutoff_time:
                            if event_type is None or event["event_type"] == event_type:
                                events.append(event)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return sorted(events, key=lambda x: x["timestamp"], reverse=True)
    
    def get_security_alerts(self, hours: int = 24) -> List[Dict]:
        """Get security alerts from recent events"""
        events = self.get_recent_events(hours)
        alerts = []
        
        # Check for suspicious patterns
        ip_activity = defaultdict(list)
        failed_logins = []
        rate_limit_violations = []
        
        for event in events:
            ip_activity[event["user_ip"]].append(event)
            
            if event["event_type"] == "admin_login" and event["status_code"] == 401:
                failed_logins.append(event)
            
            if event["event_type"] == "rate_limit_exceeded":
                rate_limit_violations.append(event)
        
        # Generate alerts
        for ip, activities in ip_activity.items():
            if len(activities) > 50:  # High activity
                alerts.append({
                    "type": "high_activity",
                    "ip": ip,
                    "count": len(activities),
                    "description": f"High activity detected from IP {ip}: {len(activities)} requests"
                })
        
        if len(failed_logins) > 10:
            alerts.append({
                "type": "failed_logins",
                "count": len(failed_logins),
                "description": f"Multiple failed login attempts: {len(failed_logins)}"
            })
        
        if rate_limit_violations:
            alerts.append({
                "type": "rate_limit_violations",
                "count": len(rate_limit_violations),
                "description": f"Rate limit violations: {len(rate_limit_violations)}"
            })
        
        return alerts

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        warnings = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif len(password) < 12:
            warnings.append("Consider using a longer password (12+ characters)")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            warnings.append("Consider adding special characters for better security")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "strength": "strong" if len(errors) == 0 and len(warnings) <= 1 else "medium" if len(errors) == 0 else "weak"
        }
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Basic input sanitization"""
        import html
        return html.escape(text.strip())
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        import secrets
        return secrets.token_urlsafe(length)

# Global instances
rate_limiter = RateLimiter()
audit_logger = AuditLogger()
security_utils = SecurityUtils() 