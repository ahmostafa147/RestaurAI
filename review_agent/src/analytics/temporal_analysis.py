"""
Temporal analysis calculator for restaurant reviews
"""
from typing import List, Dict, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
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

class TemporalAnalysisCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = reviews
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "by_day_of_week": self.analyze_by_day_of_week(),
            "by_month": self.analyze_by_month(),
            "by_time_of_day": self.analyze_by_time_of_day(),
            "trends": self.analyze_trends(),
            "review_velocity": self.calculate_velocity(),
        }
    
    def analyze_by_day_of_week(self) -> Dict[str, Any]:
        """Group reviews by weekday and calculate average rating per day"""
        day_ratings = defaultdict(list)
        day_counts = Counter()
        
        for review in self.reviews:
            try:
                if review.review_date:
                    date_obj = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    day_name = date_obj.strftime('%A')
                    day_ratings[day_name].append(review.rating)
                    day_counts[day_name] += 1
            except (ValueError, AttributeError):
                continue
        
        # Calculate averages for each day
        day_analysis = {}
        for day, ratings in day_ratings.items():
            if ratings:
                day_analysis[day] = {
                    'review_count': len(ratings),
                    'average_rating': round(statistics.mean(ratings), 2),
                    'rating_distribution': dict(Counter([str(r) for r in ratings]))
                }
        
        return day_analysis
    
    def analyze_by_month(self) -> Dict[str, Any]:
        """Group reviews by month and calculate metrics"""
        month_ratings = defaultdict(list)
        month_counts = Counter()
        
        for review in self.reviews:
            try:
                if review.review_date:
                    date_obj = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    month_key = date_obj.strftime('%Y-%m')
                    month_ratings[month_key].append(review.rating)
                    month_counts[month_key] += 1
            except (ValueError, AttributeError):
                continue
        
        # Calculate averages for each month
        month_analysis = {}
        for month, ratings in month_ratings.items():
            if ratings:
                month_analysis[month] = {
                    'review_count': len(ratings),
                    'average_rating': round(statistics.mean(ratings), 2),
                    'rating_distribution': dict(Counter([str(r) for r in ratings]))
                }
        
        return month_analysis
    
    def analyze_by_time_of_day(self) -> Dict[str, Any]:
        """Analyze ratings by time of day using visit_context"""
        time_ratings = defaultdict(list)
        time_counts = Counter()
        
        for review in self.reviews:
            if not review.llm_processed or not review.visit_context:
                continue
                
            try:
                visit_data = json.loads(review.visit_context)
                time_of_visit = visit_data.get('time_of_visit', 'unknown')
                if time_of_visit != 'unknown':
                    time_ratings[time_of_visit].append(review.rating)
                    time_counts[time_of_visit] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate averages for each time period
        time_analysis = {}
        for time_period, ratings in time_ratings.items():
            if ratings:
                time_analysis[time_period] = {
                    'review_count': len(ratings),
                    'average_rating': round(statistics.mean(ratings), 2),
                    'rating_distribution': dict(Counter([str(r) for r in ratings]))
                }
        
        return time_analysis
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze rating trends over time"""
        if not self.reviews:
            return {"trend_analysis": "insufficient_data"}
        
        # Sort reviews by date
        dated_reviews = []
        for review in self.reviews:
            try:
                if review.review_date:
                    date_obj = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    dated_reviews.append((date_obj, review.rating))
            except (ValueError, AttributeError):
                continue
        
        if len(dated_reviews) < 2:
            return {"trend_analysis": "insufficient_data"}
        
        dated_reviews.sort(key=lambda x: x[0])
        
        # Calculate simple linear trend
        dates = [review[0] for review in dated_reviews]
        ratings = [review[1] for review in dated_reviews]
        
        # Convert dates to numeric values (days since first review)
        first_date = dates[0]
        numeric_dates = [(date - first_date).days for date in dates]
        
        # Calculate trend slope
        try:
            slope = self._calculate_slope(numeric_dates, ratings)
            trend_direction = "improving" if slope > 0.01 else "declining" if slope < -0.01 else "stable"
        except:
            slope = 0.0
            trend_direction = "unknown"
        
        # Calculate recent vs early performance
        if len(ratings) >= 4:
            early_avg = statistics.mean(ratings[:len(ratings)//2])
            recent_avg = statistics.mean(ratings[len(ratings)//2:])
            performance_change = recent_avg - early_avg
        else:
            early_avg = recent_avg = performance_change = None
        
        return {
            "trend_slope": round(slope, 4),
            "trend_direction": trend_direction,
            "early_period_average": round(early_avg, 2) if early_avg else None,
            "recent_period_average": round(recent_avg, 2) if recent_avg else None,
            "performance_change": round(performance_change, 2) if performance_change is not None else None,
            "total_period_days": (dates[-1] - dates[0]).days if len(dates) > 1 else 0
        }
    
    def calculate_velocity(self) -> Dict[str, Any]:
        """Calculate review velocity (reviews per time period)"""
        if not self.reviews:
            return {"velocity_analysis": "no_data"}
        
        # Get all review dates
        review_dates = []
        for review in self.reviews:
            try:
                if review.review_date:
                    date_obj = datetime.fromisoformat(review.review_date.replace('Z', '+00:00'))
                    review_dates.append(date_obj)
            except (ValueError, AttributeError):
                continue
        
        if len(review_dates) < 2:
            return {"velocity_analysis": "insufficient_data"}
        
        review_dates.sort()
        
        # Calculate velocity metrics
        total_days = (review_dates[-1] - review_dates[0]).days
        if total_days == 0:
            return {"velocity_analysis": "single_day"}
        
        reviews_per_week = len(review_dates) / (total_days / 7)
        reviews_per_month = len(review_dates) / (total_days / 30)
        
        # Calculate velocity by month
        monthly_velocity = defaultdict(int)
        for date in review_dates:
            month_key = date.strftime('%Y-%m')
            monthly_velocity[month_key] += 1
        
        return {
            "total_reviews": len(review_dates),
            "total_days": total_days,
            "reviews_per_week": round(reviews_per_week, 2),
            "reviews_per_month": round(reviews_per_month, 2),
            "monthly_velocity": dict(monthly_velocity)
        }
    
    def _calculate_slope(self, x: List[float], y: List[float]) -> float:
        """Calculate slope of linear regression line"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denominator
