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
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_reviews": len(self.reviews),
                "processed_reviews": len(self.processed_reviews),
                "processing_coverage": round(len(self.processed_reviews) / len(self.reviews) * 100, 1) if self.reviews else 0
            },
            "basic_metrics": BasicMetricsCalculator(self.reviews).calculate_all(),
            "menu_analytics": MenuAnalyticsCalculator(self.reviews).calculate_all(),
            "staff_analytics": StaffAnalyticsCalculator(self.reviews).calculate_all(),
            "temporal_analysis": TemporalAnalysisCalculator(self.reviews).calculate_all(),
            "operational_metrics": OperationalMetricsCalculator(self.reviews).calculate_all(),
            "customer_insights": CustomerInsightsCalculator(self.reviews).calculate_all(),
            "reputation_insights": self.calculate_reputation_insights(),
        }
    
    def calculate_reputation_insights(self) -> Dict[str, Any]:
        """Calculate reputation and anomaly insights"""
        if not self.processed_reviews:
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
        
        for review in self.processed_reviews:
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
        total_processed = len(self.processed_reviews)
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
    
    def export_report(self, output_path: str, format: str = "json"):
        """Export report to file"""
        report = self.generate_full_report()
        
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of key metrics"""
        report = self.generate_full_report()
        
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
