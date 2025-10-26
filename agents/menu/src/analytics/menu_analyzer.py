from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict, Counter
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from backend.src.models.menu import MenuItem


class MenuAnalyzer:
    """Algorithmic analyzer for menu item popularity, profitability, and temporal patterns"""
    
    def __init__(self):
        self.analyzer = self
    
    def calculate_item_popularity(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Calculate popularity metrics for each menu item"""
        item_stats = defaultdict(lambda: {
            'order_count': 0,
            'total_quantity': 0,
            'hourly_distribution': defaultdict(int),
            'day_of_week': defaultdict(int),
            'monthly_distribution': defaultdict(int)
        })
        
        for ticket in tickets:
            if ticket.get('status') != 'closed':
                continue
                
            ticket_date = datetime.fromisoformat(ticket.get('created_at', ''))
            hour = ticket_date.hour
            day_of_week = ticket_date.strftime('%A')
            month = ticket_date.strftime('%Y-%m')
            
            for order in ticket.get('orders', []):
                for item in order.get('items', []):
                    item_id = item.get('id')
                    item_name = item.get('name')
                    
                    if item_id:
                        item_stats[item_id]['order_count'] += 1
                        item_stats[item_id]['total_quantity'] += 1
                        item_stats[item_id]['hourly_distribution'][hour] += 1
                        item_stats[item_id]['day_of_week'][day_of_week] += 1
                        item_stats[item_id]['monthly_distribution'][month] += 1
        
        # Convert defaultdicts to regular dicts and calculate percentages
        result = {}
        for item_id, stats in item_stats.items():
            total_orders = stats['order_count']
            result[item_id] = {
                'order_count': total_orders,
                'total_quantity': stats['total_quantity'],
                'hourly_distribution': dict(stats['hourly_distribution']),
                'day_of_week': dict(stats['day_of_week']),
                'monthly_distribution': dict(stats['monthly_distribution']),
                'peak_hour': max(stats['hourly_distribution'].items(), key=lambda x: x[1])[0] if stats['hourly_distribution'] else None,
                'most_popular_day': max(stats['day_of_week'].items(), key=lambda x: x[1])[0] if stats['day_of_week'] else None
            }
        
        return result
    
    def calculate_profit_margins(self, menu_items: List[MenuItem]) -> Dict[int, Dict[str, float]]:
        """Calculate profit margins for menu items based on ingredient costs"""
        profit_data = {}
        
        for item in menu_items:
            # Calculate total ingredient cost
            total_cost = 0.0
            ingredient_breakdown = []
            
            for ingredient in item.ingredients:
                ingredient_cost = ingredient.cost * ingredient.quantity
                total_cost += ingredient_cost
                ingredient_breakdown.append({
                    'name': ingredient.name,
                    'quantity': ingredient.quantity,
                    'unit': ingredient.unit,
                    'cost_per_unit': ingredient.cost,
                    'total_cost': ingredient_cost
                })
            
            # Calculate profit metrics
            profit_margin = ((item.price - total_cost) / item.price * 100) if item.price > 0 else 0
            profit_amount = item.price - total_cost
            
            profit_data[item.id] = {
                'item_name': item.name,
                'price': item.price,
                'total_ingredient_cost': total_cost,
                'profit_amount': profit_amount,
                'profit_margin_percentage': profit_margin,
                'ingredient_breakdown': ingredient_breakdown
            }
        
        return profit_data
    
    def analyze_temporal_patterns(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal ordering patterns"""
        hourly_orders = defaultdict(int)
        daily_orders = defaultdict(int)
        monthly_orders = defaultdict(int)
        day_of_week_orders = defaultdict(int)
        
        total_revenue = 0.0
        total_orders = 0
        
        for ticket in tickets:
            if ticket.get('status') != 'closed':
                continue
                
            ticket_date = datetime.fromisoformat(ticket.get('created_at', ''))
            hour = ticket_date.hour
            day = ticket_date.strftime('%Y-%m-%d')
            month = ticket_date.strftime('%Y-%m')
            day_of_week = ticket_date.strftime('%A')
            
            hourly_orders[hour] += 1
            daily_orders[day] += 1
            monthly_orders[month] += 1
            day_of_week_orders[day_of_week] += 1
            
            total_revenue += ticket.get('total', 0)
            total_orders += 1
        
        # Find peak times
        peak_hour = max(hourly_orders.items(), key=lambda x: x[1])[0] if hourly_orders else None
        peak_day = max(day_of_week_orders.items(), key=lambda x: x[1])[0] if day_of_week_orders else None
        peak_month = max(monthly_orders.items(), key=lambda x: x[1])[0] if monthly_orders else None
        
        return {
            'hourly_distribution': dict(hourly_orders),
            'daily_distribution': dict(daily_orders),
            'monthly_distribution': dict(monthly_orders),
            'day_of_week_distribution': dict(day_of_week_orders),
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'peak_month': peak_month,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_order_value': total_revenue / total_orders if total_orders > 0 else 0
        }
    
    def calculate_revenue_metrics(self, tickets: List[Dict], menu_items: List[MenuItem]) -> Dict[int, Dict[str, float]]:
        """Calculate revenue metrics per menu item"""
        item_revenue = defaultdict(lambda: {
            'total_revenue': 0.0,
            'order_count': 0,
            'average_order_value': 0.0
        })
        
        for ticket in tickets:
            if ticket.get('status') != 'closed':
                continue
                
            for order in ticket.get('orders', []):
                for item in order.get('items', []):
                    item_id = item.get('id')
                    if item_id:
                        item_revenue[item_id]['total_revenue'] += item.get('price', 0)
                        item_revenue[item_id]['order_count'] += 1
        
        # Calculate averages
        for item_id, stats in item_revenue.items():
            if stats['order_count'] > 0:
                stats['average_order_value'] = stats['total_revenue'] / stats['order_count']
        
        return dict(item_revenue)
    
    def analyze_menu_performance(self, tickets: List[Dict], menu_items: List[MenuItem]) -> Dict[str, Any]:
        """Comprehensive menu performance analysis"""
        popularity = self.calculate_item_popularity(tickets)
        profit_margins = self.calculate_profit_margins(menu_items)
        temporal_patterns = self.analyze_temporal_patterns(tickets)
        revenue_metrics = self.calculate_revenue_metrics(tickets, menu_items)
        
        # Find top and bottom performers
        sorted_by_orders = sorted(popularity.items(), key=lambda x: x[1]['order_count'], reverse=True)
        sorted_by_profit = sorted(profit_margins.items(), key=lambda x: x[1]['profit_margin_percentage'], reverse=True)
        sorted_by_revenue = sorted(revenue_metrics.items(), key=lambda x: x[1]['total_revenue'], reverse=True)
        
        return {
            'popularity_metrics': popularity,
            'profit_margins': profit_margins,
            'temporal_patterns': temporal_patterns,
            'revenue_metrics': revenue_metrics,
            'top_performers': {
                'by_orders': sorted_by_orders[:5],
                'by_profit_margin': sorted_by_profit[:5],
                'by_revenue': sorted_by_revenue[:5]
            },
            'bottom_performers': {
                'by_orders': sorted_by_orders[-5:] if len(sorted_by_orders) > 5 else sorted_by_orders,
                'by_profit_margin': sorted_by_profit[-5:] if len(sorted_by_profit) > 5 else sorted_by_profit,
                'by_revenue': sorted_by_revenue[-5:] if len(sorted_by_revenue) > 5 else sorted_by_revenue
            }
        }
