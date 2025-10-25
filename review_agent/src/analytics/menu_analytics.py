"""
Menu analytics calculator for restaurant reviews
"""
from typing import List, Dict, Any
from collections import defaultdict, Counter
import json

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

class MenuAnalyticsCalculator:
    def __init__(self, reviews: List[Review]):
        self.reviews = [r for r in reviews if r.llm_processed and r.mentioned_items]
    
    def calculate_all(self) -> Dict[str, Any]:
        return {
            "items": self.get_all_items(),
            "top_praised": self.get_top_praised_items(limit=10),
            "top_criticized": self.get_top_criticized_items(limit=10),
            "aspect_analysis": self.analyze_aspects(),
        }
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Parse mentioned_items JSON and aggregate by name"""
        item_data = defaultdict(lambda: {
            'mention_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'mixed_count': 0,
            'aspects': Counter()
        })
        
        for review in self.reviews:
            try:
                if review.mentioned_items:
                    items = json.loads(review.mentioned_items)
                    for item in items:
                        name = item.get('name', '').strip().lower()
                        if not name:
                            continue
                            
                        item_data[name]['mention_count'] += 1
                        sentiment = item.get('sentiment', '').lower()
                        
                        if sentiment == 'positive':
                            item_data[name]['positive_count'] += 1
                        elif sentiment == 'negative':
                            item_data[name]['negative_count'] += 1
                        elif sentiment == 'mixed':
                            item_data[name]['mixed_count'] += 1
                        
                        # Track aspects
                        aspects = item.get('aspects', [])
                        for aspect in aspects:
                            item_data[name]['aspects'][aspect] += 1
                            
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Convert to list and calculate sentiment scores
        items_list = []
        for name, data in item_data.items():
            total_mentions = data['mention_count']
            if total_mentions == 0:
                continue
                
            # Calculate sentiment score (-1 to 1)
            positive_ratio = data['positive_count'] / total_mentions
            negative_ratio = data['negative_count'] / total_mentions
            sentiment_score = positive_ratio - negative_ratio
            
            items_list.append({
                'name': name.title(),
                'mention_count': total_mentions,
                'positive_count': data['positive_count'],
                'negative_count': data['negative_count'],
                'mixed_count': data['mixed_count'],
                'sentiment_score': round(sentiment_score, 2),
                'aspects': dict(data['aspects'])
            })
        
        # Sort by mention count
        items_list.sort(key=lambda x: x['mention_count'], reverse=True)
        return items_list
    
    def get_top_praised_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get items with highest positive sentiment"""
        all_items = self.get_all_items()
        # Filter items with at least 2 mentions and positive sentiment
        praised_items = [
            item for item in all_items 
            if item['mention_count'] >= 2 and item['sentiment_score'] > 0
        ]
        return praised_items[:limit]
    
    def get_top_criticized_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get items with lowest sentiment scores"""
        all_items = self.get_all_items()
        # Filter items with at least 2 mentions and negative sentiment
        criticized_items = [
            item for item in all_items 
            if item['mention_count'] >= 2 and item['sentiment_score'] < 0
        ]
        # Sort by sentiment score (most negative first)
        criticized_items.sort(key=lambda x: x['sentiment_score'])
        return criticized_items[:limit]
    
    def analyze_aspects(self) -> Dict[str, Any]:
        """Analyze sentiment by aspect (taste, portion, presentation, temperature, price)"""
        aspect_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'mixed': 0})
        aspect_mentions = Counter()
        
        for review in self.reviews:
            try:
                if review.mentioned_items:
                    items = json.loads(review.mentioned_items)
                    for item in items:
                        sentiment = item.get('sentiment', '').lower()
                        aspects = item.get('aspects', [])
                        
                        for aspect in aspects:
                            aspect_mentions[aspect] += 1
                            if sentiment == 'positive':
                                aspect_sentiment[aspect]['positive'] += 1
                            elif sentiment == 'negative':
                                aspect_sentiment[aspect]['negative'] += 1
                            elif sentiment == 'mixed':
                                aspect_sentiment[aspect]['mixed'] += 1
                                
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Calculate sentiment scores for each aspect
        aspect_analysis = {}
        for aspect, counts in aspect_sentiment.items():
            total = sum(counts.values())
            if total > 0:
                positive_ratio = counts['positive'] / total
                negative_ratio = counts['negative'] / total
                sentiment_score = positive_ratio - negative_ratio
                
                aspect_analysis[aspect] = {
                    'mention_count': aspect_mentions[aspect],
                    'positive_count': counts['positive'],
                    'negative_count': counts['negative'],
                    'mixed_count': counts['mixed'],
                    'sentiment_score': round(sentiment_score, 2)
                }
        
        return aspect_analysis
