"""
Operational metrics calculator for restaurant reviews
"""
from typing import List, Dict, Any
from collections import Counter, defaultdict
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

class OperationalMetricsCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = [r for r in reviews if r.llm_processed]
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "ambiance_ratings": self.analyze_ambiance(),
            "wait_time_patterns": self.analyze_wait_times(),
            "cleanliness_scores": self.analyze_cleanliness(),
            "noise_level_distribution": self.analyze_noise_levels(),
            "crowding_patterns": self.analyze_crowding(),
        }
    
    def analyze_ambiance(self) -> Dict[str, Any]:
        """Analyze ambiance ratings and distribution"""
        ambiance_ratings = []
        for review in self.reviews:
            if review.rating_ambiance is not None:
                ambiance_ratings.append(review.rating_ambiance)
        
        if not ambiance_ratings:
            return {"analysis": "no_ambiance_ratings_available"}
        
        rating_distribution = Counter(ambiance_ratings)
        
        return {
            "average_rating": round(statistics.mean(ambiance_ratings), 2),
            "rating_distribution": dict(rating_distribution),
            "total_ratings": len(ambiance_ratings),
            "rating_percentage": {
                str(rating): round(count / len(ambiance_ratings) * 100, 1)
                for rating, count in rating_distribution.items()
            }
        }
    
    def analyze_wait_times(self) -> Dict[str, Any]:
        """Analyze wait time patterns from operational_insights"""
        wait_time_data = []
        wait_time_distribution = Counter()
        
        for review in self.reviews:
            if not review.operational_insights:
                continue
                
            try:
                insights = json.loads(review.operational_insights)
                wait_time = insights.get('wait_time', 'not_mentioned')
                if wait_time != 'not_mentioned':
                    wait_time_data.append(wait_time)
                    wait_time_distribution[wait_time] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        if not wait_time_data:
            return {"analysis": "no_wait_time_data_available"}
        
        # Calculate percentages
        total_mentions = len(wait_time_data)
        wait_time_percentages = {
            wait_type: round(count / total_mentions * 100, 1)
            for wait_type, count in wait_time_distribution.items()
        }
        
        return {
            "total_mentions": total_mentions,
            "distribution": dict(wait_time_distribution),
            "percentages": wait_time_percentages,
            "most_common": wait_time_distribution.most_common(1)[0] if wait_time_distribution else None
        }
    
    def analyze_cleanliness(self) -> Dict[str, Any]:
        """Analyze cleanliness mentions from operational_insights"""
        cleanliness_data = []
        cleanliness_distribution = Counter()
        
        for review in self.reviews:
            if not review.operational_insights:
                continue
                
            try:
                insights = json.loads(review.operational_insights)
                cleanliness = insights.get('cleanliness', 'not_mentioned')
                if cleanliness != 'not_mentioned':
                    cleanliness_data.append(cleanliness)
                    cleanliness_distribution[cleanliness] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        if not cleanliness_data:
            return {"analysis": "no_cleanliness_data_available"}
        
        # Calculate percentages
        total_mentions = len(cleanliness_data)
        cleanliness_percentages = {
            cleanliness_type: round(count / total_mentions * 100, 1)
            for cleanliness_type, count in cleanliness_distribution.items()
        }
        
        return {
            "total_mentions": total_mentions,
            "distribution": dict(cleanliness_distribution),
            "percentages": cleanliness_percentages,
            "most_common": cleanliness_distribution.most_common(1)[0] if cleanliness_distribution else None
        }
    
    def analyze_noise_levels(self) -> Dict[str, Any]:
        """Analyze noise level distribution from operational_insights"""
        noise_data = []
        noise_distribution = Counter()
        
        for review in self.reviews:
            if not review.operational_insights:
                continue
                
            try:
                insights = json.loads(review.operational_insights)
                noise_level = insights.get('noise_level', 'not_mentioned')
                if noise_level != 'not_mentioned':
                    noise_data.append(noise_level)
                    noise_distribution[noise_level] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        if not noise_data:
            return {"analysis": "no_noise_level_data_available"}
        
        # Calculate percentages
        total_mentions = len(noise_data)
        noise_percentages = {
            noise_type: round(count / total_mentions * 100, 1)
            for noise_type, count in noise_distribution.items()
        }
        
        return {
            "total_mentions": total_mentions,
            "distribution": dict(noise_distribution),
            "percentages": noise_percentages,
            "most_common": noise_distribution.most_common(1)[0] if noise_distribution else None
        }
    
    def analyze_crowding(self) -> Dict[str, Any]:
        """Analyze crowding patterns from operational_insights"""
        crowding_data = []
        crowding_distribution = Counter()
        
        for review in self.reviews:
            if not review.operational_insights:
                continue
                
            try:
                insights = json.loads(review.operational_insights)
                crowding = insights.get('crowding', 'not_mentioned')
                if crowding != 'not_mentioned':
                    crowding_data.append(crowding)
                    crowding_distribution[crowding] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        if not crowding_data:
            return {"analysis": "no_crowding_data_available"}
        
        # Calculate percentages
        total_mentions = len(crowding_data)
        crowding_percentages = {
            crowding_type: round(count / total_mentions * 100, 1)
            for crowding_type, count in crowding_distribution.items()
        }
        
        return {
            "total_mentions": total_mentions,
            "distribution": dict(crowding_distribution),
            "percentages": crowding_percentages,
            "most_common": crowding_distribution.most_common(1)[0] if crowding_distribution else None
        }
