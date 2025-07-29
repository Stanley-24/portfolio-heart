import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import geoip2.database
import geoip2.errors
import os
import logging

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Advanced analytics tracker for user behavior and performance metrics"""
    
    def __init__(self):
        self.events: List[Dict] = []
        self.page_views: Dict[str, int] = defaultdict(int)
        self.user_sessions: Dict[str, Dict] = {}
        self.conversions: Dict[str, int] = defaultdict(int)
        self.performance_metrics: List[Dict] = []
        self.geographic_data: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "sessions": 0})
        
        # Initialize GeoIP database if available
        self.geoip_reader = None
        try:
            geoip_path = os.getenv("GEOIP_DATABASE_PATH", "GeoLite2-City.mmdb")
            if os.path.exists(geoip_path):
                self.geoip_reader = geoip2.database.Reader(geoip_path)
                logger.info("GeoIP database loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load GeoIP database: {e}")
    
    def track_page_view(self, page: str, user_ip: str, user_agent: str, 
                       referrer: Optional[str] = None, session_id: Optional[str] = None):
        """Track a page view with geographic and user data"""
        timestamp = datetime.utcnow()
        
        # Get geographic data
        geo_data = self._get_geographic_data(user_ip)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = self._generate_session_id(user_ip, user_agent)
        
        # Track page view
        self.page_views[page] += 1
        
        # Track geographic data
        if geo_data:
            country = geo_data.get("country", "Unknown")
            city = geo_data.get("city", "Unknown")
            location_key = f"{country}/{city}"
            self.geographic_data[location_key]["count"] += 1
        
        # Track session
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                "start_time": timestamp,
                "pages": [],
                "user_ip": user_ip,
                "user_agent": user_agent,
                "geo_data": geo_data
            }
        
        self.user_sessions[session_id]["pages"].append({
            "page": page,
            "timestamp": timestamp,
            "referrer": referrer
        })
        
        # Log event
        event = {
            "type": "page_view",
            "timestamp": timestamp.isoformat(),
            "page": page,
            "user_ip": user_ip,
            "session_id": session_id,
            "geo_data": geo_data,
            "referrer": referrer
        }
        self.events.append(event)
    
    def track_conversion(self, conversion_type: str, user_ip: str, user_agent: str,
                        session_id: Optional[str] = None, metadata: Optional[Dict] = None):
        """Track conversion events (contact, booking, review, etc.)"""
        timestamp = datetime.utcnow()
        
        # Get geographic data
        geo_data = self._get_geographic_data(user_ip)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = self._generate_session_id(user_ip, user_agent)
        
        # Track conversion
        self.conversions[conversion_type] += 1
        
        # Track geographic data for conversions
        if geo_data:
            country = geo_data.get("country", "Unknown")
            city = geo_data.get("city", "Unknown")
            location_key = f"{country}/{city}"
            if "conversions" not in self.geographic_data[location_key]:
                self.geographic_data[location_key]["conversions"] = defaultdict(int)
            self.geographic_data[location_key]["conversions"][conversion_type] += 1
        
        # Log event
        event = {
            "type": "conversion",
            "timestamp": timestamp.isoformat(),
            "conversion_type": conversion_type,
            "user_ip": user_ip,
            "session_id": session_id,
            "geo_data": geo_data,
            "metadata": metadata or {}
        }
        self.events.append(event)
    
    def track_performance(self, endpoint: str, response_time: float, status_code: int,
                         user_ip: str, user_agent: str):
        """Track API performance metrics"""
        timestamp = datetime.utcnow()
        
        performance_data = {
            "timestamp": timestamp.isoformat(),
            "endpoint": endpoint,
            "response_time": response_time,
            "status_code": status_code,
            "user_ip": user_ip,
            "user_agent": user_agent
        }
        
        self.performance_metrics.append(performance_data)
        
        # Keep only last 1000 performance records
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    def track_user_behavior(self, action: str, user_ip: str, user_agent: str,
                           session_id: Optional[str] = None, data: Optional[Dict] = None):
        """Track user behavior events"""
        timestamp = datetime.utcnow()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = self._generate_session_id(user_ip, user_agent)
        
        event = {
            "type": "user_behavior",
            "timestamp": timestamp.isoformat(),
            "action": action,
            "user_ip": user_ip,
            "session_id": session_id,
            "data": data or {}
        }
        self.events.append(event)
    
    def _get_geographic_data(self, ip_address: str) -> Optional[Dict]:
        """Get geographic data for an IP address"""
        if not self.geoip_reader or ip_address in ["127.0.0.1", "localhost", "unknown"]:
            return None
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                "country": response.country.name,
                "country_code": response.country.iso_code,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone
            }
        except (geoip2.errors.AddressNotFoundError, geoip2.errors.GeoIP2Error):
            return None
        except Exception as e:
            logger.error(f"Error getting geographic data for {ip_address}: {e}")
            return None
    
    def _generate_session_id(self, user_ip: str, user_agent: str) -> str:
        """Generate a unique session ID"""
        data = f"{user_ip}:{user_agent}:{int(time.time() / 3600)}"  # Hour-based
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events by time
        recent_events = [e for e in self.events 
                        if datetime.fromisoformat(e["timestamp"]) >= cutoff_time]
        
        # Page views
        page_views = defaultdict(int)
        for event in recent_events:
            if event["type"] == "page_view":
                page_views[event["page"]] += 1
        
        # Conversions
        conversions = defaultdict(int)
        for event in recent_events:
            if event["type"] == "conversion":
                conversions[event["conversion_type"]] += 1
        
        # Geographic data
        geo_summary = {}
        for location, data in self.geographic_data.items():
            if data["count"] > 0:
                geo_summary[location] = {
                    "page_views": data["count"],
                    "conversions": dict(data.get("conversions", {})),
                    "conversion_rate": self._calculate_conversion_rate(data["count"], data.get("conversions", {}))
                }
        
        # Performance metrics
        recent_performance = [p for p in self.performance_metrics 
                            if datetime.fromisoformat(p["timestamp"]) >= cutoff_time]
        
        avg_response_time = 0
        if recent_performance:
            avg_response_time = sum(p["response_time"] for p in recent_performance) / len(recent_performance)
        
        # User sessions
        active_sessions = [s for s in self.user_sessions.values() 
                          if s["start_time"] >= cutoff_time]
        
        return {
            "time_period": f"Last {hours} hours",
            "total_page_views": sum(page_views.values()),
            "total_conversions": sum(conversions.values()),
            "conversion_rate": self._calculate_overall_conversion_rate(page_views, conversions),
            "page_views": dict(page_views),
            "conversions": dict(conversions),
            "geographic_data": geo_summary,
            "performance": {
                "avg_response_time": round(avg_response_time, 3),
                "total_requests": len(recent_performance),
                "error_rate": self._calculate_error_rate(recent_performance)
            },
            "sessions": {
                "total_sessions": len(active_sessions),
                "avg_session_duration": self._calculate_avg_session_duration(active_sessions),
                "avg_pages_per_session": self._calculate_avg_pages_per_session(active_sessions)
            },
            "top_pages": sorted(page_views.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_conversions": sorted(conversions.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_locations": sorted(geo_summary.items(), key=lambda x: x[1]["page_views"], reverse=True)[:10]
        }
    
    def get_geographic_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed geographic analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events by time
        recent_events = [e for e in self.events 
                        if datetime.fromisoformat(e["timestamp"]) >= cutoff_time]
        
        # Group by country
        country_data = defaultdict(lambda: {
            "page_views": 0,
            "conversions": defaultdict(int),
            "cities": defaultdict(int),
            "sessions": set()
        })
        
        for event in recent_events:
            if event.get("geo_data"):
                country = event["geo_data"]["country"]
                city = event["geo_data"]["city"]
                session_id = event.get("session_id")
                
                country_data[country]["sessions"].add(session_id)
                
                if event["type"] == "page_view":
                    country_data[country]["page_views"] += 1
                    country_data[country]["cities"][city] += 1
                elif event["type"] == "conversion":
                    conversion_type = event["conversion_type"]
                    country_data[country]["conversions"][conversion_type] += 1
        
        # Format data for response
        formatted_data = {}
        for country, data in country_data.items():
            formatted_data[country] = {
                "page_views": data["page_views"],
                "unique_sessions": len(data["sessions"]),
                "conversions": dict(data["conversions"]),
                "conversion_rate": self._calculate_conversion_rate(data["page_views"], data["conversions"]),
                "top_cities": sorted(data["cities"].items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        return {
            "time_period": f"Last {hours} hours",
            "countries": formatted_data,
            "total_countries": len(formatted_data),
            "top_countries": sorted(formatted_data.items(), 
                                  key=lambda x: x[1]["page_views"], reverse=True)[:10]
        }
    
    def get_performance_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed performance analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter performance metrics by time
        recent_performance = [p for p in self.performance_metrics 
                            if datetime.fromisoformat(p["timestamp"]) >= cutoff_time]
        
        if not recent_performance:
            return {"error": "No performance data available"}
        
        # Group by endpoint
        endpoint_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "status_codes": defaultdict(int),
            "response_times": []
        })
        
        for metric in recent_performance:
            endpoint = metric["endpoint"]
            endpoint_stats[endpoint]["count"] += 1
            endpoint_stats[endpoint]["total_time"] += metric["response_time"]
            endpoint_stats[endpoint]["status_codes"][metric["status_code"]] += 1
            endpoint_stats[endpoint]["response_times"].append(metric["response_time"])
        
        # Calculate statistics for each endpoint
        endpoint_analytics = {}
        for endpoint, stats in endpoint_stats.items():
            avg_time = stats["total_time"] / stats["count"]
            response_times = sorted(stats["response_times"])
            median_time = response_times[len(response_times) // 2]
            
            endpoint_analytics[endpoint] = {
                "request_count": stats["count"],
                "avg_response_time": round(avg_time, 3),
                "median_response_time": round(median_time, 3),
                "min_response_time": round(min(stats["response_times"]), 3),
                "max_response_time": round(max(stats["response_times"]), 3),
                "error_rate": self._calculate_endpoint_error_rate(stats["status_codes"]),
                "status_codes": dict(stats["status_codes"])
            }
        
        # Overall statistics
        all_response_times = [m["response_time"] for m in recent_performance]
        overall_avg = sum(all_response_times) / len(all_response_times)
        
        return {
            "time_period": f"Last {hours} hours",
            "total_requests": len(recent_performance),
            "overall_avg_response_time": round(overall_avg, 3),
            "endpoints": endpoint_analytics,
            "top_slowest_endpoints": sorted(endpoint_analytics.items(), 
                                          key=lambda x: x[1]["avg_response_time"], reverse=True)[:10],
            "top_most_used_endpoints": sorted(endpoint_analytics.items(), 
                                            key=lambda x: x[1]["request_count"], reverse=True)[:10]
        }
    
    def get_user_behavior_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get user behavior analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter events by time
        recent_events = [e for e in self.events 
                        if datetime.fromisoformat(e["timestamp"]) >= cutoff_time]
        
        # User behavior events
        behavior_events = [e for e in recent_events if e["type"] == "user_behavior"]
        
        # Group by action
        action_counts = Counter(e["action"] for e in behavior_events)
        
        # Session analysis
        active_sessions = [s for s in self.user_sessions.values() 
                          if s["start_time"] >= cutoff_time]
        
        # Calculate session metrics
        session_durations = []
        pages_per_session = []
        
        for session in active_sessions:
            if len(session["pages"]) > 1:
                duration = (session["pages"][-1]["timestamp"] - session["pages"][0]["timestamp"]).total_seconds()
                session_durations.append(duration)
            pages_per_session.append(len(session["pages"]))
        
        # User journey analysis
        user_journeys = defaultdict(list)
        for session in active_sessions:
            if len(session["pages"]) > 1:
                journey = [p["page"] for p in session["pages"]]
                user_journeys[tuple(journey)].append(session)
        
        return {
            "time_period": f"Last {hours} hours",
            "total_behavior_events": len(behavior_events),
            "action_breakdown": dict(action_counts),
            "sessions": {
                "total_sessions": len(active_sessions),
                "avg_session_duration": round(sum(session_durations) / len(session_durations), 2) if session_durations else 0,
                "avg_pages_per_session": round(sum(pages_per_session) / len(pages_per_session), 2) if pages_per_session else 0,
                "bounce_rate": self._calculate_bounce_rate(active_sessions)
            },
            "user_journeys": {
                "total_unique_journeys": len(user_journeys),
                "most_common_journeys": sorted(user_journeys.items(), 
                                             key=lambda x: len(x[1]), reverse=True)[:10]
            }
        }
    
    def _calculate_conversion_rate(self, page_views: int, conversions: Dict) -> float:
        """Calculate conversion rate"""
        total_conversions = sum(conversions.values())
        return round((total_conversions / page_views * 100), 2) if page_views > 0 else 0
    
    def _calculate_overall_conversion_rate(self, page_views: Dict, conversions: Dict) -> float:
        """Calculate overall conversion rate"""
        total_views = sum(page_views.values())
        total_conversions = sum(conversions.values())
        return round((total_conversions / total_views * 100), 2) if total_views > 0 else 0
    
    def _calculate_error_rate(self, performance_metrics: List[Dict]) -> float:
        """Calculate error rate from performance metrics"""
        if not performance_metrics:
            return 0
        error_count = sum(1 for m in performance_metrics if m["status_code"] >= 400)
        return round((error_count / len(performance_metrics) * 100), 2)
    
    def _calculate_endpoint_error_rate(self, status_codes: Dict) -> float:
        """Calculate error rate for a specific endpoint"""
        total_requests = sum(status_codes.values())
        error_requests = sum(count for code, count in status_codes.items() if code >= 400)
        return round((error_requests / total_requests * 100), 2) if total_requests > 0 else 0
    
    def _calculate_avg_session_duration(self, sessions: List[Dict]) -> float:
        """Calculate average session duration"""
        durations = []
        for session in sessions:
            if len(session["pages"]) > 1:
                duration = (session["pages"][-1]["timestamp"] - session["pages"][0]["timestamp"]).total_seconds()
                durations.append(duration)
        return round(sum(durations) / len(durations), 2) if durations else 0
    
    def _calculate_avg_pages_per_session(self, sessions: List[Dict]) -> float:
        """Calculate average pages per session"""
        if not sessions:
            return 0
        total_pages = sum(len(session["pages"]) for session in sessions)
        return round(total_pages / len(sessions), 2)
    
    def _calculate_bounce_rate(self, sessions: List[Dict]) -> float:
        """Calculate bounce rate (sessions with only one page view)"""
        if not sessions:
            return 0.0
        
        single_page_sessions = sum(1 for session in sessions if len(session["pages"]) == 1)
        return (single_page_sessions / len(sessions)) * 100

# Initialize the analytics tracker
analytics_tracker = AnalyticsTracker() 