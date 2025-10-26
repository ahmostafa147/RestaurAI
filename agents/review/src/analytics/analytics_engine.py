"""
Main analytics engine for restaurant review analysis
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import Counter
import json

# Handle imports with proper path resolution
try:
    from ..models.review import Review
    from ..storage.database_handler import DatabaseHandler
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)
    from models.review import Review
    from storage.database_handler import DatabaseHandler

from .basic_metrics import BasicMetricsCalculator
from .menu_analytics import MenuAnalyticsCalculator
from .staff_analytics import StaffAnalyticsCalculator
from .temporal_analysis import TemporalAnalysisCalculator
from .operational_metrics import OperationalMetricsCalculator
from .customer_insights import CustomerInsightsCalculator

class AnalyticsEngine:
    def __init__(self, database_handler: DatabaseHandler):
        self.db = database_handler
        self.reviews = self.db.get_all_reviews()
        self.processed_reviews = [r for r in self.reviews if r.llm_processed]
    
    def generate_full_report(self, restaurant_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive analytics report for a specific restaurant or all restaurants"""
        
        # Filter reviews by restaurant if specified
        reviews_to_analyze = self.reviews
        processed_reviews_to_analyze = self.processed_reviews
        
        if restaurant_id:
            reviews_to_analyze = self.db.get_reviews_by_restaurant(restaurant_id)
            processed_reviews_to_analyze = [r for r in reviews_to_analyze if r.llm_processed]
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_reviews": len(reviews_to_analyze),
                "processed_reviews": len(processed_reviews_to_analyze),
                "processing_coverage": round(len(processed_reviews_to_analyze) / len(reviews_to_analyze) * 100, 1) if reviews_to_analyze else 0
            },
            "basic_metrics": BasicMetricsCalculator(reviews_to_analyze).calculate_all(),
            "menu_analytics": MenuAnalyticsCalculator(reviews_to_analyze).calculate_all(),
            "staff_analytics": StaffAnalyticsCalculator(reviews_to_analyze).calculate_all(),
            "temporal_analysis": TemporalAnalysisCalculator(reviews_to_analyze).calculate_all(),
            "operational_metrics": OperationalMetricsCalculator(reviews_to_analyze).calculate_all(),
            "customer_insights": CustomerInsightsCalculator(reviews_to_analyze).calculate_all(),
            "reputation_insights": self._calculate_reputation_insights_for_reviews(processed_reviews_to_analyze),
        }
    
    def generate_multi_restaurant_report(self) -> Dict[str, Any]:
        """Generate analytics report for all restaurants"""
        
        # Get unique restaurant IDs from reviews
        restaurant_ids = set()
        restaurant_names = {}
        for review in self.reviews:
            if hasattr(review, 'restaurant_id') and review.restaurant_id:
                restaurant_ids.add(review.restaurant_id)
                if hasattr(review, 'restaurant_name') and review.restaurant_name:
                    restaurant_names[review.restaurant_id] = review.restaurant_name
        
        # If no restaurant IDs found, return a report for all reviews
        if not restaurant_ids:
            return {
                "generated_at": datetime.now().isoformat(),
                "restaurants": {
                    "default": {
                        "id": "default",
                        "name": "Default",
                        "analytics": self.generate_full_report()
                    }
                }
            }
        
        # Generate report for each restaurant
        restaurants_report = {}
        for restaurant_id in restaurant_ids:
            analytics = self.generate_full_report(restaurant_id=restaurant_id)
            restaurants_report[restaurant_id] = {
                "id": restaurant_id,
                "name": restaurant_names.get(restaurant_id, restaurant_id),
                "analytics": analytics
            }
        
        return {
            "generated_at": datetime.now().isoformat(),
            "restaurants": restaurants_report
        }
    
    def _calculate_reputation_insights_for_reviews(self, processed_reviews) -> Dict[str, Any]:
        """Calculate reputation insights for a specific set of reviews"""
        if not processed_reviews:
            return {"analysis": "no_processed_reviews"}
        
        # Analyze anomaly flags
        anomaly_data = {
            'potential_fake': 0,
            'health_safety_concern': 0,
            'extreme_emotion': 0,
            'competitor_mention': 0
        }
        
        sentiment_distribution = Counter()
        key_phrases_positive = []
        key_phrases_negative = []
        
        for review in processed_reviews:
            # Count anomaly flags
            if review.anomaly_flags:
                try:
                    flags = json.loads(review.anomaly_flags)
                    for flag, value in flags.items():
                        if value and flag in anomaly_data:
                            anomaly_data[flag] += 1
                except (json.JSONDecodeError, AttributeError, TypeError):
                    pass
            
            # Track sentiment
            if review.overall_sentiment:
                sentiment_distribution[review.overall_sentiment] += 1
            
            # Collect key phrases
            if review.key_phrases:
                try:
                    phrases = json.loads(review.key_phrases)
                    key_phrases_positive.extend(phrases.get('positive_highlights', []))
                    key_phrases_negative.extend(phrases.get('negative_issues', []))
                except (json.JSONDecodeError, AttributeError, TypeError):
                    pass
        
        # Calculate anomaly percentages
        total_processed = len(processed_reviews)
        anomaly_percentages = {
            flag: round(count / total_processed * 100, 1)
            for flag, count in anomaly_data.items()
        }
        
        # Get most common key phrases
        positive_phrase_counts = Counter(key_phrases_positive)
        negative_phrase_counts = Counter(key_phrases_negative)
        
        return {
            "anomaly_flags": anomaly_data,
            "anomaly_percentages": anomaly_percentages,
            "sentiment_distribution": dict(sentiment_distribution),
            "top_positive_phrases": dict(positive_phrase_counts.most_common(10)),
            "top_negative_phrases": dict(negative_phrase_counts.most_common(10)),
            "total_positive_phrases": len(key_phrases_positive),
            "total_negative_phrases": len(key_phrases_negative)
        }
    
    def export_report(self, output_path: str, format: str = "json", multi_restaurant: bool = True):
        """Export report to file"""
        if multi_restaurant:
            report = self.generate_multi_restaurant_report()
        else:
            report = self.generate_full_report()
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_summary(self, restaurant_id: str = None) -> Dict[str, Any]:
        """Get a summary of key metrics"""
        report = self.generate_full_report(restaurant_id=restaurant_id)
        
        basic_metrics = report.get('basic_metrics', {})
        overall_perf = basic_metrics.get('overall_performance', {})
        
        return {
            "total_reviews": overall_perf.get('total_reviews', 0),
            "processed_reviews": overall_perf.get('processed_reviews', 0),
            "average_rating": overall_perf.get('average_rating', 0.0),
            "review_velocity": overall_perf.get('review_velocity', 0.0),
            "menu_items_mentioned": len(report.get('menu_analytics', {}).get('items', [])),
            "staff_members_mentioned": len(report.get('staff_analytics', {}).get('by_person', [])),
            "processing_coverage": report.get('metadata', {}).get('processing_coverage', 0.0)
        }
