"""
Basic metrics calculator for restaurant reviews
"""
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
import statistics

# Handle imports with proper path resolution
try:
    from ..models.review import Review
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from models.review import Review

class BasicMetricsCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = reviews
        self.processed_reviews = [r for r in reviews if r.llm_processed]
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "overall_performance": self.calculate_overall_performance(),
            "rating_breakdown": self.calculate_rating_breakdown(),
            "platform_comparison": self.calculate_platform_comparison(),
            "response_metrics": self.calculate_response_metrics(),
        }
    
    def calculate_overall_performance(self) -> Dict[str, Any]:
        """Calculate basic performance metrics"""
        if not self.reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "processed_reviews": 0,
                "review_velocity": 0.0
            }
        
        ratings = [r.rating for r in self.reviews if r.rating is not None]
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        
        # Calculate review velocity (reviews per week)
        review_dates = []
        for review in self.reviews:
            try:
                if review.review_date:
                    date_obj = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    review_dates.append(date_obj)
            except (ValueError, AttributeError):
                continue
        
        velocity = 0.0
        if len(review_dates) > 1:
            review_dates.sort()
            time_span = (review_dates[-1] - review_dates[0]).days
            if time_span > 0:
                velocity = len(review_dates) / (time_span / 7)  # reviews per week
        
        return {
            "total_reviews": len(self.reviews),
            "average_rating": round(avg_rating, 2),
            "processed_reviews": len(self.processed_reviews),
            "review_velocity": round(velocity, 2)
        }
    
    def calculate_rating_breakdown(self) -> Dict[str, Any]:
        """Calculate rating distribution and aspect ratings"""
        if not self.reviews:
            return {
                "rating_distribution": {},
                "aspect_ratings": {}
            }
        
        # Overall rating distribution
        rating_dist = Counter()
        for review in self.reviews:
            if review.rating is not None:
                rating_dist[str(review.rating)] += 1
        
        # Aspect ratings (food, service, ambiance, value)
        aspect_ratings = {
            "food": [],
            "service": [],
            "ambiance": [],
            "value": []
        }
        
        for review in self.processed_reviews:
            if review.rating_food is not None:
                aspect_ratings["food"].append(review.rating_food)
            if review.rating_service is not None:
                aspect_ratings["service"].append(review.rating_service)
            if review.rating_ambiance is not None:
                aspect_ratings["ambiance"].append(review.rating_ambiance)
            if review.rating_value is not None:
                aspect_ratings["value"].append(review.rating_value)
        
        # Calculate averages for each aspect
        aspect_averages = {}
        for aspect, ratings in aspect_ratings.items():
            if ratings:
                aspect_averages[aspect] = round(statistics.mean(ratings), 2)
            else:
                aspect_averages[aspect] = None
        
        return {
            "rating_distribution": dict(rating_dist),
            "aspect_ratings": aspect_averages
        }
    
    def calculate_platform_comparison(self) -> Dict[str, Any]:
        """Compare metrics across platforms (Google vs Yelp)"""
        if not self.reviews:
            return {"platforms": {}}
        
        platform_data = {}
        for review in self.reviews:
            platform = review.source
            if platform not in platform_data:
                platform_data[platform] = {
                    "count": 0,
                    "ratings": [],
                    "response_count": 0,
                    "processed_count": 0
                }
            
            platform_data[platform]["count"] += 1
            if review.rating is not None:
                platform_data[platform]["ratings"].append(review.rating)
            if review.response_from_owner:
                platform_data[platform]["response_count"] += 1
            if review.llm_processed:
                platform_data[platform]["processed_count"] += 1
        
        # Calculate averages and response rates
        for platform, data in platform_data.items():
            if data["ratings"]:
                data["average_rating"] = round(statistics.mean(data["ratings"]), 2)
            else:
                data["average_rating"] = None
            
            if data["count"] > 0:
                data["response_rate"] = round(data["response_count"] / data["count"], 3)
            else:
                data["response_rate"] = 0.0
            
            # Remove raw ratings list to keep output clean
            del data["ratings"]
        
        return {"platforms": platform_data}
    
    def calculate_response_metrics(self) -> Dict[str, Any]:
        """Calculate response-related metrics"""
        if not self.reviews:
            return {
                "response_rate": 0.0,
                "total_responses": 0,
                "response_times": []
            }
        
        total_reviews = len(self.reviews)
        responses = [r for r in self.reviews if r.response_from_owner]
        response_rate = len(responses) / total_reviews if total_reviews > 0 else 0.0
        
        # Calculate response times (if we have both review_date and owner_response_date)
        response_times = []
        for review in responses:
            try:
                if review.review_date and review.owner_response_date:
                    review_date = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    response_date = datetime.fromisoformat(review.owner_response_date.replace('Z', '+00:00'))
                    days_diff = (response_date - review_date).days
                    response_times.append(days_diff)
            except (ValueError, AttributeError):
                continue
        
        avg_response_time = statistics.mean(response_times) if response_times else None
        
        return {
            "response_rate": round(response_rate, 3),
            "total_responses": len(responses),
            "average_response_time_days": round(avg_response_time, 1) if avg_response_time else None
        }
