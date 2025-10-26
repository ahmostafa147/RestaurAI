"""
Customer insights calculator for restaurant reviews
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

class CustomerInsightsCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = [r for r in reviews if r.llm_processed]
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "segmentation": self.analyze_segmentation(),
            "loyalty_metrics": self.analyze_loyalty(),
            "value_perception": self.analyze_value_perception(),
            "occasion_analysis": self.analyze_occasions(),
        }
    
    def analyze_segmentation(self) -> Dict[str, Any]:
        """Analyze customer segments by party_type"""
        segment_data = defaultdict(list)
        segment_counts = Counter()
        
        for review in self.reviews:
            if not review.visit_context:
                continue
                
            try:
                visit_data = json.loads(review.visit_context)
                party_type = visit_data.get('party_type', 'unknown')
                if party_type != 'unknown':
                    segment_data[party_type].append(review.rating)
                    segment_counts[party_type] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate metrics for each segment
        segment_analysis = {}
        for segment, ratings in segment_data.items():
            if ratings:
                segment_analysis[segment] = {
                    'review_count': len(ratings),
                    'average_rating': round(statistics.mean(ratings), 2),
                    'rating_distribution': dict(Counter([str(r) for r in ratings])),
                    'percentage_of_total': round(len(ratings) / len(self.reviews) * 100, 1)
                }
        
        return {
            "segments": segment_analysis,
            "total_segmented_reviews": sum(segment_counts.values()),
            "segmentation_coverage": round(sum(segment_counts.values()) / len(self.reviews) * 100, 1) if self.reviews else 0
        }
    
    def analyze_loyalty(self) -> Dict[str, Any]:
        """Analyze loyalty metrics from visit_context"""
        loyalty_data = {
            'first_visit': {'yes': 0, 'no': 0, 'unknown': 0},
            'would_return': {'yes': 0, 'no': 0, 'unknown': 0},
            'would_recommend': {'yes': 0, 'no': 0, 'unknown': 0}
        }
        
        loyalty_ratings = defaultdict(list)
        
        for review in self.reviews:
            if not review.visit_context:
                continue
                
            try:
                visit_data = json.loads(review.visit_context)
                
                # Track first visit
                first_visit = visit_data.get('first_visit')
                if first_visit is not None:
                    loyalty_data['first_visit']['yes' if first_visit else 'no'] += 1
                else:
                    loyalty_data['first_visit']['unknown'] += 1
                
                # Track return intention
                would_return = visit_data.get('would_return')
                if would_return is not None:
                    loyalty_data['would_return']['yes' if would_return else 'no'] += 1
                    loyalty_ratings['would_return'].append((would_return, review.rating))
                else:
                    loyalty_data['would_return']['unknown'] += 1
                
                # Track recommendation intention
                would_recommend = visit_data.get('would_recommend')
                if would_recommend is not None:
                    loyalty_data['would_recommend']['yes' if would_recommend else 'no'] += 1
                    loyalty_ratings['would_recommend'].append((would_recommend, review.rating))
                else:
                    loyalty_data['would_recommend']['unknown'] += 1
                    
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate loyalty percentages
        loyalty_percentages = {}
        for metric, data in loyalty_data.items():
            total = sum(data.values())
            if total > 0:
                loyalty_percentages[metric] = {
                    'yes_percentage': round(data['yes'] / total * 100, 1),
                    'no_percentage': round(data['no'] / total * 100, 1),
                    'unknown_percentage': round(data['unknown'] / total * 100, 1)
                }
            else:
                loyalty_percentages[metric] = {'yes_percentage': 0, 'no_percentage': 0, 'unknown_percentage': 0}
        
        # Calculate rating correlations with loyalty
        loyalty_correlations = {}
        for metric, ratings in loyalty_ratings.items():
            if len(ratings) >= 2:
                yes_ratings = [r[1] for r in ratings if r[0]]
                no_ratings = [r[1] for r in ratings if not r[0]]
                
                loyalty_correlations[metric] = {
                    'yes_average_rating': round(statistics.mean(yes_ratings), 2) if yes_ratings else None,
                    'no_average_rating': round(statistics.mean(no_ratings), 2) if no_ratings else None,
                    'rating_difference': round(statistics.mean(yes_ratings) - statistics.mean(no_ratings), 2) if yes_ratings and no_ratings else None
                }
        
        return {
            "loyalty_data": loyalty_data,
            "loyalty_percentages": loyalty_percentages,
            "loyalty_correlations": loyalty_correlations
        }
    
    def analyze_value_perception(self) -> Dict[str, Any]:
        """Analyze value perception using rating_value"""
        value_ratings = []
        value_by_rating = defaultdict(list)
        
        for review in self.reviews:
            if review.rating_value is not None:
                value_ratings.append(review.rating_value)
                value_by_rating[review.rating_value].append(review.rating)
        
        if not value_ratings:
            return {"analysis": "no_value_ratings_available"}
        
        # Calculate value perception metrics
        value_distribution = Counter(value_ratings)
        value_percentages = {
            str(rating): round(count / len(value_ratings) * 100, 1)
            for rating, count in value_distribution.items()
        }
        
        # Calculate correlation between value rating and overall rating
        value_correlations = {}
        for value_rating, overall_ratings in value_by_rating.items():
            if overall_ratings:
                value_correlations[str(value_rating)] = {
                    'average_overall_rating': round(statistics.mean(overall_ratings), 2),
                    'count': len(overall_ratings)
                }
        
        return {
            "average_value_rating": round(statistics.mean(value_ratings), 2),
            "value_distribution": dict(value_distribution),
            "value_percentages": value_percentages,
            "value_correlations": value_correlations,
            "total_value_ratings": len(value_ratings)
        }
    
    def analyze_occasions(self) -> Dict[str, Any]:
        """Analyze occasion-based patterns"""
        occasion_data = defaultdict(list)
        occasion_counts = Counter()
        
        for review in self.reviews:
            if not review.visit_context:
                continue
                
            try:
                visit_data = json.loads(review.visit_context)
                occasion = visit_data.get('occasion', 'unknown')
                if occasion != 'unknown':
                    occasion_data[occasion].append(review.rating)
                    occasion_counts[occasion] += 1
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate metrics for each occasion
        occasion_analysis = {}
        for occasion, ratings in occasion_data.items():
            if ratings:
                occasion_analysis[occasion] = {
                    'review_count': len(ratings),
                    'average_rating': round(statistics.mean(ratings), 2),
                    'rating_distribution': dict(Counter([str(r) for r in ratings])),
                    'percentage_of_total': round(len(ratings) / len(self.reviews) * 100, 1)
                }
        
        return {
            "occasions": occasion_analysis,
            "total_occasion_reviews": sum(occasion_counts.values()),
            "occasion_coverage": round(sum(occasion_counts.values()) / len(self.reviews) * 100, 1) if self.reviews else 0
        }
