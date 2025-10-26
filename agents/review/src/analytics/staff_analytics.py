"""
Staff analytics calculator for restaurant reviews
"""
from typing import List, Dict, Any
from collections import defaultdict, Counter
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

class StaffAnalyticsCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = [r for r in reviews if r.llm_processed and r.staff_mentions]
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "by_person": self.get_staff_by_person(),
            "by_role": self.get_staff_by_role(),
            "top_performers": self.get_top_performers(limit=10),
            "service_rating_correlation": self.analyze_service_correlation(),
        }
    
    def get_staff_by_person(self) -> List[Dict[str, Any]]:
        """Aggregate mentions by staff name"""
        staff_data = defaultdict(lambda: {
            'mention_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'roles': set(),
            'specific_feedback': []
        })
        
        for review in self.reviews:
            try:
                if review.staff_mentions:
                    staff_mentions = json.loads(review.staff_mentions)
                    for mention in staff_mentions:
                        name = mention.get('name', '').strip()
                        if not name:
                            continue
                            
                        staff_data[name]['mention_count'] += 1
                        staff_data[name]['roles'].add(mention.get('role', 'unknown'))
                        
                        sentiment = mention.get('sentiment', '').lower()
                        if sentiment == 'positive':
                            staff_data[name]['positive_count'] += 1
                        elif sentiment == 'negative':
                            staff_data[name]['negative_count'] += 1
                        
                        # Collect specific feedback
                        feedback = mention.get('specific_feedback', '').strip()
                        if feedback:
                            staff_data[name]['specific_feedback'].append(feedback)
                            
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Convert to list and calculate metrics
        staff_list = []
        for name, data in staff_data.items():
            total_mentions = data['mention_count']
            if total_mentions == 0:
                continue
                
            # Calculate average sentiment (-1 to 1)
            positive_ratio = data['positive_count'] / total_mentions
            negative_ratio = data['negative_count'] / total_mentions
            average_sentiment = positive_ratio - negative_ratio
            
            # Get primary role (most common)
            primary_role = max(data['roles'], key=lambda r: r) if data['roles'] else 'unknown'
            
            staff_list.append({
                'name': name,
                'role': primary_role,
                'mention_count': total_mentions,
                'positive_count': data['positive_count'],
                'negative_count': data['negative_count'],
                'average_sentiment': round(average_sentiment, 2),
                'roles': list(data['roles']),
                'specific_feedback': data['specific_feedback'][:5]  # Limit to 5 examples
            })
        
        # Sort by mention count
        staff_list.sort(key=lambda x: x['mention_count'], reverse=True)
        return staff_list
    
    def get_staff_by_role(self) -> Dict[str, Any]:
        """Group by role and calculate average sentiment"""
        role_data = defaultdict(lambda: {
            'mention_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'staff_members': set()
        })
        
        for review in self.reviews:
            try:
                if review.staff_mentions:
                    staff_mentions = json.loads(review.staff_mentions)
                    for mention in staff_mentions:
                        role = mention.get('role', 'unknown')
                        name = mention.get('name', '').strip()
                        
                        role_data[role]['mention_count'] += 1
                        if name:
                            role_data[role]['staff_members'].add(name)
                        
                        sentiment = mention.get('sentiment', '').lower()
                        if sentiment == 'positive':
                            role_data[role]['positive_count'] += 1
                        elif sentiment == 'negative':
                            role_data[role]['negative_count'] += 1
                            
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate metrics for each role
        role_analysis = {}
        for role, data in role_data.items():
            total_mentions = data['mention_count']
            if total_mentions == 0:
                continue
                
            positive_ratio = data['positive_count'] / total_mentions
            negative_ratio = data['negative_count'] / total_mentions
            average_sentiment = positive_ratio - negative_ratio
            
            role_analysis[role] = {
                'mention_count': total_mentions,
                'positive_count': data['positive_count'],
                'negative_count': data['negative_count'],
                'average_sentiment': round(average_sentiment, 2),
                'staff_count': len(data['staff_members'])
            }
        
        return role_analysis
    
    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get staff with highest positive sentiment"""
        staff_list = self.get_staff_by_person()
        # Filter staff with at least 2 mentions and positive sentiment
        top_performers = [
            staff for staff in staff_list 
            if staff['mention_count'] >= 2 and staff['average_sentiment'] > 0
        ]
        # Sort by average sentiment
        top_performers.sort(key=lambda x: x['average_sentiment'], reverse=True)
        return top_performers[:limit]
    
    def analyze_service_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between service ratings and staff mentions"""
        service_ratings = []
        staff_mention_counts = []
        
        for review in self.reviews:
            # Get service rating
            service_rating = review.rating_service
            if service_rating is None:
                continue
                
            # Count staff mentions
            staff_count = 0
            try:
                if review.staff_mentions:
                    staff_mentions = json.loads(review.staff_mentions)
                    staff_count = len(staff_mentions)
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
            
            service_ratings.append(service_rating)
            staff_mention_counts.append(staff_count)
        
        if len(service_ratings) < 2:
            return {
                "correlation": None,
                "sample_size": len(service_ratings),
                "avg_service_rating": None,
                "avg_staff_mentions": None
            }
        
        # Calculate correlation coefficient (simple Pearson correlation)
        try:
            correlation = self._calculate_correlation(service_ratings, staff_mention_counts)
        except:
            correlation = None
        
        return {
            "correlation": round(correlation, 3) if correlation is not None else None,
            "sample_size": len(service_ratings),
            "avg_service_rating": round(statistics.mean(service_ratings), 2),
            "avg_staff_mentions": round(statistics.mean(staff_mention_counts), 2)
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
