"""
Algorithmic analysis of ingredient consumption patterns and stock predictions
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import statistics

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.database import db
from src.core.ingredient_manager import IngredientManager
from src.core.order_manager import OrderManager
from src.models.ingredient import Ingredient


class ConsumptionAnalyzer:
    """Analyzes historical consumption patterns and predicts stock depletion"""
    
    def __init__(self):
        """Initialize the consumption analyzer"""
        pass
    
    def analyze_consumption_patterns(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Analyze consumption patterns from historical order data
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Dictionary with consumption analysis per ingredient
        """
        # Get historical closed tickets
        closed_tickets = db.get_events(restaurant_key, "closed_ticket")
        
        if not closed_tickets:
            return {"error": "No historical order data found"}
        
        # Initialize consumption tracking
        ingredient_consumption = defaultdict(list)  # ingredient_id -> [usage_events]
        hourly_consumption = defaultdict(lambda: defaultdict(float))  # ingredient_id -> hour -> usage
        daily_consumption = defaultdict(lambda: defaultdict(float))  # ingredient_id -> day_of_week -> usage
        
        # Process each closed ticket
        for ticket_event in closed_tickets:
            ticket_data = ticket_event['data']
            orders = ticket_data.get('orders', [])
            ticket_time = datetime.fromisoformat(ticket_event['meta']['timestamp'])
            
            # Process each order in the ticket
            for order in orders:
                items = order.get('items', [])
                for item in items:
                    ingredients = item.get('ingredients', [])
                    for ingredient in ingredients:
                        ingredient_id = str(ingredient['id'])  # Convert to string for consistency
                        quantity_used = ingredient['quantity']
                        
                        # Track consumption
                        ingredient_consumption[ingredient_id].append({
                            'quantity': quantity_used,
                            'timestamp': ticket_time,
                            'hour': ticket_time.hour,
                            'day_of_week': ticket_time.weekday(),
                            'menu_item': item['name']
                        })
                        
                        # Track hourly and daily patterns
                        hourly_consumption[ingredient_id][ticket_time.hour] += quantity_used
                        daily_consumption[ingredient_id][ticket_time.weekday()] += quantity_used
        
        # Calculate consumption statistics per ingredient
        consumption_analysis = {}
        
        for ingredient_id, usage_events in ingredient_consumption.items():
            if not usage_events:
                continue
                
            quantities = [event['quantity'] for event in usage_events]
            timestamps = [event['timestamp'] for event in usage_events]
            
            # Calculate basic statistics
            total_usage = sum(quantities)
            avg_usage_per_order = statistics.mean(quantities)
            usage_volatility = statistics.stdev(quantities) if len(quantities) > 1 else 0
            
            # Calculate time-based patterns
            time_span = max(timestamps) - min(timestamps)
            days_span = max(time_span.days, 1)  # Avoid division by zero
            
            avg_daily_usage = total_usage / days_span
            avg_hourly_usage = total_usage / (days_span * 24)
            
            # Find peak usage hours
            hourly_usage = hourly_consumption[ingredient_id]
            peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Find peak usage days
            daily_usage = daily_consumption[ingredient_id]
            peak_days = sorted(daily_usage.items(), key=lambda x: x[1], reverse=True)[:2]
            
            # Get menu items that use this ingredient
            menu_items = list(set(event['menu_item'] for event in usage_events))
            
            consumption_analysis[str(ingredient_id)] = {
                'total_usage': total_usage,
                'avg_usage_per_order': avg_usage_per_order,
                'usage_volatility': usage_volatility,
                'avg_daily_usage': avg_daily_usage,
                'avg_hourly_usage': avg_hourly_usage,
                'peak_hours': [hour for hour, _ in peak_hours],
                'peak_days': [day for day, _ in peak_days],
                'menu_items': menu_items,
                'usage_events_count': len(usage_events),
                'time_span_days': days_span
            }
        
        return {
            'per_ingredient': consumption_analysis,
            'total_tickets_analyzed': len(closed_tickets),
            'analysis_period_days': max([(max(event['timestamp'] for event in events) - min(event['timestamp'] for event in events)).days 
                                       for events in ingredient_consumption.values() if events], default=0)
        }
    
    def predict_stockout_time(self, ingredient_id: int, current_quantity: float, 
                            consumption_rate: float, unit: str) -> datetime:
        """
        Predict when an ingredient will run out based on current stock and consumption rate
        
        Args:
            ingredient_id: Ingredient identifier
            current_quantity: Current stock quantity
            consumption_rate: Usage rate per hour
            unit: Unit of measurement
            
        Returns:
            Predicted datetime when stock will run out
        """
        if consumption_rate <= 0:
            # If no consumption, assume it will last indefinitely
            return datetime.now() + timedelta(days=365)
        
        # Calculate hours until stockout
        hours_until_stockout = current_quantity / consumption_rate
        
        # Add some buffer time (e.g., 2 hours) to account for variability
        hours_until_stockout += 2
        
        return datetime.now() + timedelta(hours=hours_until_stockout)
    
    def get_low_stock_warnings(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Get warnings for ingredients predicted to run out before end of next day
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of warning dictionaries for low stock ingredients
        """
        # Get current inventory
        ingredient_manager = IngredientManager(restaurant_key)
        inventory = ingredient_manager.inventory
        
        if not inventory:
            return []
        
        # Get consumption analysis
        consumption_data = self.analyze_consumption_patterns(restaurant_key)
        
        if 'error' in consumption_data:
            return []
        
        warnings = []
        end_of_next_day = datetime.now() + timedelta(days=1, hours=23, minutes=59)
        
        for ingredient_id, ingredient in inventory.items():
            ingredient_id_str = str(ingredient_id)
            
            # Skip if no consumption data
            if ingredient_id_str not in consumption_data['per_ingredient']:
                continue
            
            consumption_info = consumption_data['per_ingredient'][ingredient_id_str]
            avg_hourly_usage = consumption_info['avg_hourly_usage']
            
            # Skip if no usage
            if avg_hourly_usage <= 0:
                continue
            
            # Predict stockout time
            predicted_stockout = self.predict_stockout_time(
                int(ingredient_id),  # Convert back to int for the method
                ingredient.quantity, 
                avg_hourly_usage,
                ingredient.unit
            )
            
            # Check if stockout is predicted before end of next day
            if predicted_stockout <= end_of_next_day:
                # Calculate severity based on time until stockout
                hours_until_stockout = (predicted_stockout - datetime.now()).total_seconds() / 3600
                
                if hours_until_stockout <= 6:
                    severity = "critical"
                elif hours_until_stockout <= 12:
                    severity = "high"
                elif hours_until_stockout <= 24:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Calculate days remaining
                days_remaining = hours_until_stockout / 24
                
                warning = {
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient.name,
                    'current_quantity': ingredient.quantity,
                    'unit': ingredient.unit,
                    'severity': severity,
                    'predicted_runout': predicted_stockout.isoformat(),
                    'consumption_rate': avg_hourly_usage,
                    'days_remaining': days_remaining,
                    'supplier': ingredient.supplier,
                    'cost_per_unit': ingredient.cost,
                    'usage_volatility': consumption_info['usage_volatility'],
                    'menu_items_affected': consumption_info['menu_items']
                }
                
                warnings.append(warning)
        
        # Sort by severity and time until stockout
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        warnings.sort(key=lambda x: (severity_order[x['severity']], x['predicted_runout']))
        
        return warnings
    
    def get_consumption_forecast(self, restaurant_key: str, ingredient_id: int, 
                               hours_ahead: int = 48) -> Dict[str, Any]:
        """
        Generate consumption forecast for a specific ingredient
        
        Args:
            restaurant_key: Restaurant identifier
            ingredient_id: Ingredient to forecast
            hours_ahead: Hours to forecast ahead (default 48)
            
        Returns:
            Forecast data including predicted usage and confidence
        """
        consumption_data = self.analyze_consumption_patterns(restaurant_key)
        ingredient_id_str = str(ingredient_id)
        
        if ingredient_id_str not in consumption_data['per_ingredient']:
            return {'error': 'No consumption data for ingredient'}
        
        consumption_info = consumption_data['per_ingredient'][ingredient_id_str]
        avg_hourly_usage = consumption_info['avg_hourly_usage']
        usage_volatility = consumption_info['usage_volatility']
        
        # Calculate predicted usage
        predicted_usage_24h = avg_hourly_usage * 24
        predicted_usage_48h = avg_hourly_usage * 48
        
        # Calculate confidence based on data quality and volatility
        data_points = consumption_info['usage_events_count']
        time_span = consumption_info['time_span_days']
        
        # Higher confidence with more data points and longer time span
        data_confidence = min(1.0, (data_points / 50) * (time_span / 30))
        
        # Lower confidence with high volatility
        volatility_factor = max(0.1, 1.0 - (usage_volatility / avg_hourly_usage))
        
        confidence_level = data_confidence * volatility_factor
        
        # Get peak usage hours
        peak_hours = consumption_info['peak_hours']
        
        return {
            'ingredient_id': ingredient_id,
            'predicted_usage_24h': predicted_usage_24h,
            'predicted_usage_48h': predicted_usage_48h,
            'confidence_level': confidence_level,
            'peak_usage_hours': peak_hours,
            'avg_hourly_usage': avg_hourly_usage,
            'usage_volatility': usage_volatility,
            'data_points': data_points,
            'time_span_days': time_span
        }
