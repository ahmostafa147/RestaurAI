from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from .models import LLMInsights


class ReportGenerator:
    """Generates comprehensive menu analytics reports"""
    
    def __init__(self):
        self.generator = self
    
    def generate_comprehensive_report(
        self, 
        restaurant_key: str,
        menu_data: Dict,
        algorithmic_results: Dict,
        llm_insights: LLMInsights,
        review_analytics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive menu analytics report"""
        
        # Extract data from results
        popularity_metrics = algorithmic_results.get('popularity_metrics', {})
        profit_margins = algorithmic_results.get('profit_margins', {})
        temporal_patterns = algorithmic_results.get('temporal_patterns', {})
        revenue_metrics = algorithmic_results.get('revenue_metrics', {})
        top_performers = algorithmic_results.get('top_performers', {})
        bottom_performers = algorithmic_results.get('bottom_performers', {})
        
        # Generate individual menu item analysis
        menu_items_analysis = self._analyze_menu_items(
            menu_data, popularity_metrics, profit_margins, 
            revenue_metrics, llm_insights, review_analytics
        )
        
        # Generate overall insights
        overall_insights = self._generate_overall_insights(
            temporal_patterns, top_performers, bottom_performers, 
            llm_insights, review_analytics
        )
        
        # Create metadata
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'restaurant_key': restaurant_key,
            'total_menu_items': len(menu_items_analysis),
            'analysis_period': self._get_analysis_period(temporal_patterns),
            'data_sources': self._get_data_sources(review_analytics)
        }
        
        return {
            'metadata': metadata,
            'menu_items': menu_items_analysis,
            'overall_insights': overall_insights,
            'summary_metrics': self._generate_summary_metrics(
                popularity_metrics, profit_margins, temporal_patterns
            )
        }
    
    def _analyze_menu_items(
        self, 
        menu_data: Dict, 
        popularity_metrics: Dict, 
        profit_margins: Dict,
        revenue_metrics: Dict,
        llm_insights: Dict,
        review_analytics: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Analyze individual menu items"""
        
        items_analysis = []
        
        # Get all menu items
        all_items = []
        for category, items in menu_data.items():
            for item in items:
                all_items.append((item, category))
        
        for item, category in all_items:
            item_id = item.get('id')
            
            # Popularity data
            popularity = popularity_metrics.get(item_id, {})
            
            # Financial data
            profit_data = profit_margins.get(item_id, {})
            revenue_data = revenue_metrics.get(item_id, {})
            
            # LLM insights for this item
            prep_insights = llm_insights.preparation_insights.get(str(item_id))
            
            # Review sentiment
            sentiment = self._get_item_sentiment(item.get('name'), review_analytics)
            
            # Day-part analysis from LLM insights
            item_day_part = llm_insights.day_part_analysis.per_item.get(str(item_id), {})
            
            item_analysis = {
                'item_id': item_id,
                'name': item.get('name'),
                'category': category,
                'price': item.get('price'),
                'available': item.get('available', True),
                'popularity': {
                    'order_count': popularity.get('order_count', 0),
                    'total_quantity': popularity.get('total_quantity', 0),
                    'peak_hour': popularity.get('peak_hour'),
                    'most_popular_day': popularity.get('most_popular_day'),
                    'hourly_distribution': popularity.get('hourly_distribution', {}),
                    'day_of_week': popularity.get('day_of_week', {}),
                    'monthly_distribution': popularity.get('monthly_distribution', {})
                },
                'financial': {
                    'revenue': revenue_data.get('total_revenue', 0),
                    'order_count': revenue_data.get('order_count', 0),
                    'average_order_value': revenue_data.get('average_order_value', 0),
                    'cost': profit_data.get('total_ingredient_cost', 0),
                    'profit_amount': profit_data.get('profit_amount', 0),
                    'profit_margin_percentage': profit_data.get('profit_margin_percentage', 0),
                    'ingredient_breakdown': profit_data.get('ingredient_breakdown', [])
                },
                'temporal': {
                    'hourly_distribution': popularity.get('hourly_distribution', {}),
                    'day_part_analysis': {
                        'primary_day_part': item_day_part.primary_day_part.value if hasattr(item_day_part, 'primary_day_part') else 'unknown',
                        'day_part_distribution': item_day_part.day_part_distribution.dict() if hasattr(item_day_part, 'day_part_distribution') else {},
                        'rationale': item_day_part.rationale if hasattr(item_day_part, 'rationale') else ''
                    },
                    'primary_day_part': item_day_part.primary_day_part.value if hasattr(item_day_part, 'primary_day_part') else 'unknown'
                },
                'review_sentiment': sentiment,
                'llm_insights': {
                    'estimated_prep_time_minutes': prep_insights.estimated_prep_time_minutes if hasattr(prep_insights, 'estimated_prep_time_minutes') else 0,
                    'complexity_level': prep_insights.complexity_level.value if hasattr(prep_insights, 'complexity_level') else 'unknown',
                    'prep_notes': prep_insights.prep_notes if hasattr(prep_insights, 'prep_notes') else '',
                    'cooking_methods': prep_insights.cooking_methods if hasattr(prep_insights, 'cooking_methods') else [],
                    'prep_breakdown': prep_insights.prep_breakdown.dict() if hasattr(prep_insights, 'prep_breakdown') else {},
                    'kitchen_efficiency_notes': prep_insights.kitchen_efficiency_notes if hasattr(prep_insights, 'kitchen_efficiency_notes') else '',
                    'suggestions': self._get_item_suggestions(item_id, llm_insights)
                }
            }
            
            items_analysis.append(item_analysis)
        
        return items_analysis
    
    def _generate_overall_insights(
        self, 
        temporal_patterns: Dict, 
        top_performers: Dict, 
        bottom_performers: Dict,
        llm_insights: Dict,
        review_analytics: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate overall insights and recommendations"""
        
        return {
            'business_hours_analysis': {
                'peak_hour': temporal_patterns.get('peak_hour'),
                'peak_day': temporal_patterns.get('peak_day'),
                'peak_month': temporal_patterns.get('peak_month'),
                'total_revenue': temporal_patterns.get('total_revenue', 0),
                'total_orders': temporal_patterns.get('total_orders', 0),
                'average_order_value': temporal_patterns.get('average_order_value', 0)
            },
            'performance_rankings': {
                'top_by_orders': top_performers.get('by_orders', []),
                'top_by_profit': top_performers.get('by_profit_margin', []),
                'top_by_revenue': top_performers.get('by_revenue', []),
                'bottom_by_orders': bottom_performers.get('by_orders', []),
                'bottom_by_profit': bottom_performers.get('by_profit_margin', []),
                'bottom_by_revenue': bottom_performers.get('by_revenue', [])
            },
            'llm_recommendations': {
                'trend_observations': llm_insights.trend_observations,
                'actionable_suggestions': llm_insights.actionable_suggestions,
                'day_part_analysis': llm_insights.day_part_analysis.dict(),
                'sentiment_integration': llm_insights.sentiment_integration.dict()
            },
            'review_integration': self._integrate_review_insights(review_analytics)
        }
    
    def _generate_summary_metrics(
        self, 
        popularity_metrics: Dict, 
        profit_margins: Dict, 
        temporal_patterns: Dict
    ) -> Dict[str, Any]:
        """Generate summary metrics"""
        
        total_items = len(popularity_metrics)
        total_orders = sum(item.get('order_count', 0) for item in popularity_metrics.values())
        total_revenue = temporal_patterns.get('total_revenue', 0)
        
        # Calculate average metrics
        avg_profit_margin = 0
        if profit_margins:
            avg_profit_margin = sum(
                item.get('profit_margin_percentage', 0) 
                for item in profit_margins.values()
            ) / len(profit_margins)
        
        return {
            'total_menu_items': total_items,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': temporal_patterns.get('average_order_value', 0),
            'average_profit_margin': round(avg_profit_margin, 2),
            'most_popular_item': self._find_most_popular_item(popularity_metrics),
            'highest_profit_item': self._find_highest_profit_item(profit_margins),
            'busiest_hour': temporal_patterns.get('peak_hour'),
            'busiest_day': temporal_patterns.get('peak_day')
        }
    
    
    def _get_item_sentiment(self, item_name: str, review_analytics: Optional[Dict]) -> Dict[str, Any]:
        """Get sentiment data for a specific item"""
        if not review_analytics:
            return {'sentiment_score': 0, 'mentions': 0, 'feedback': []}
        
        menu_analytics = review_analytics.get('menu_analytics', {})
        items = menu_analytics.get('items', [])
        
        for item in items:
            if item.get('name', '').lower() == item_name.lower():
                return {
                    'sentiment_score': item.get('sentiment_score', 0),
                    'mentions': item.get('mention_count', 0),
                    'positive_count': item.get('positive_count', 0),
                    'negative_count': item.get('negative_count', 0),
                    'aspects': item.get('aspects', {})
                }
        
        return {'sentiment_score': 0, 'mentions': 0, 'feedback': []}
    
    def _get_item_suggestions(self, item_id: int, llm_insights: Dict) -> List[str]:
        """Get suggestions for a specific item"""
        # This would be extracted from LLM insights
        # For now, return empty list
        return []
    
    def _integrate_review_insights(self, review_analytics: Optional[Dict]) -> Dict[str, Any]:
        """Integrate review analytics insights"""
        if not review_analytics:
            return {'integration_available': False}
        
        return {
            'integration_available': True,
            'top_praised_items': review_analytics.get('menu_analytics', {}).get('top_praised', []),
            'top_criticized_items': review_analytics.get('menu_analytics', {}).get('top_criticized', []),
            'aspect_analysis': review_analytics.get('menu_analytics', {}).get('aspect_analysis', {}),
            'sentiment_distribution': review_analytics.get('reputation_insights', {}).get('sentiment_distribution', {})
        }
    
    def _find_most_popular_item(self, popularity_metrics: Dict) -> Dict[str, Any]:
        """Find the most popular item"""
        if not popularity_metrics:
            return {'name': 'N/A', 'orders': 0}
        
        most_popular = max(popularity_metrics.items(), key=lambda x: x[1].get('order_count', 0))
        return {
            'name': most_popular[1].get('name', 'Unknown'),
            'orders': most_popular[1].get('order_count', 0)
        }
    
    def _find_highest_profit_item(self, profit_margins: Dict) -> Dict[str, Any]:
        """Find the highest profit margin item"""
        if not profit_margins:
            return {'name': 'N/A', 'margin': 0}
        
        highest_profit = max(profit_margins.items(), key=lambda x: x[1].get('profit_margin_percentage', 0))
        return {
            'name': highest_profit[1].get('item_name', 'Unknown'),
            'margin': highest_profit[1].get('profit_margin_percentage', 0)
        }
    
    def _get_analysis_period(self, temporal_patterns: Dict) -> Dict[str, str]:
        """Get the analysis period from temporal data"""
        monthly_dist = temporal_patterns.get('monthly_distribution', {})
        if monthly_dist:
            months = sorted(monthly_dist.keys())
            return {
                'start_month': months[0] if months else 'Unknown',
                'end_month': months[-1] if months else 'Unknown'
            }
        return {'start_month': 'Unknown', 'end_month': 'Unknown'}
    
    def _get_data_sources(self, review_analytics: Optional[Dict]) -> List[str]:
        """Get list of data sources used"""
        sources = ['ticket_logs', 'menu_data', 'inventory_data']
        if review_analytics:
            sources.append('review_analytics')
        return sources
