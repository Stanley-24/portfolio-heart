from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import rate_limiter, audit_logger
import time
import json

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for rate limiting and audit logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Determine endpoint for rate limiting
        endpoint = self._get_endpoint_key(request)
        
        # Check rate limiting
        if rate_limiter.is_rate_limited(request, endpoint):
            # Log rate limit violation
            audit_logger.log_event(
                event_type="rate_limit_exceeded",
                user_ip=client_ip,
                user_agent=user_agent,
                endpoint=str(request.url.path),
                method=request.method,
                status_code=429,
                request_data=self._get_request_data(request),
                admin_action=endpoint.startswith("admin_")
            )
            
            # Return rate limit response
            remaining_info = rate_limiter.get_remaining_requests(request, endpoint)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {int(remaining_info['reset_time'] - time.time())} seconds.",
                    "remaining_requests": remaining_info["remaining"],
                    "limit": remaining_info["limit"],
                    "reset_time": remaining_info["reset_time"]
                }
            )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "message": str(e)}
            )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log the event
        audit_logger.log_event(
            event_type=self._get_event_type(request, status_code),
            user_ip=client_ip,
            user_agent=user_agent,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=status_code,
            request_data=self._get_request_data(request),
            response_data=self._get_response_data(response) if status_code < 400 else None,
            user_id=self._get_user_id(request),
            admin_action=endpoint.startswith("admin_")
        )
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Response-Time"] = f"{response_time:.3f}s"
        
        # Add rate limit headers
        remaining_info = rate_limiter.get_remaining_requests(request, endpoint)
        response.headers["X-RateLimit-Limit"] = str(remaining_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(remaining_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(remaining_info["reset_time"]))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_key(self, request: Request) -> str:
        """Get endpoint key for rate limiting"""
        path = request.url.path
        
        # Map specific endpoints to rate limit keys
        if path.startswith("/api/contact/send-message"):
            return "contact_send_message"
        elif path.startswith("/api/contact/book-call"):
            return "contact_book_call"
        elif path.startswith("/api/reviews") and request.method == "POST":
            return "review_create"
        elif path.startswith("/api/newsletter/subscribe"):
            return "newsletter_subscribe"
        elif path.startswith("/api/resume/download"):
            return "resume_download"
        elif path.startswith("/api/auth/login"):
            return "admin_login"
        elif path.startswith("/api/auth/change-password"):
            return "admin_change_password"
        elif path.startswith("/api/admin"):
            return "admin_general"
        else:
            return "api_general"
    
    def _get_event_type(self, request: Request, status_code: int) -> str:
        """Get event type for audit logging"""
        path = request.url.path
        
        if path.startswith("/api/auth/login"):
            return "admin_login"
        elif path.startswith("/api/auth/change-password"):
            return "admin_change_password"
        elif path.startswith("/api/contact/send-message"):
            return "contact_message"
        elif path.startswith("/api/contact/book-call"):
            return "call_booking"
        elif path.startswith("/api/reviews"):
            return "review_action"
        elif path.startswith("/api/newsletter/subscribe"):
            return "newsletter_subscription"
        elif path.startswith("/api/resume/download"):
            return "resume_download"
        elif path.startswith("/api/admin"):
            return "admin_action"
        elif status_code >= 400:
            return "error"
        else:
            return "api_request"
    
    def _get_request_data(self, request: Request) -> dict:
        """Get sanitized request data for logging"""
        try:
            # Only log basic info, not sensitive data
            return {
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "headers": {
                    k: v for k, v in request.headers.items() 
                    if k.lower() not in ["authorization", "cookie", "x-api-key"]
                }
            }
        except Exception:
            return {"error": "Could not parse request data"}
    
    def _get_response_data(self, response: Response) -> dict:
        """Get sanitized response data for logging"""
        try:
            if hasattr(response, 'body'):
                # Only log response size, not content
                return {
                    "status_code": response.status_code,
                    "content_length": len(response.body) if response.body else 0
                }
            return {"status_code": response.status_code}
        except Exception:
            return {"error": "Could not parse response data"}
    
    def _get_user_id(self, request: Request) -> str:
        """Get user ID from request (if available)"""
        # This would be extracted from JWT token or session
        # For now, return None
        return None 