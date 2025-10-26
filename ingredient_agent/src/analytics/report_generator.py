"""
Report generator for ingredient agent analytics
"""

import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .models import LLMInsights, StockWarning, ReorderSuggestion, InventoryReport
from .consumption_analyzer import ConsumptionAnalyzer
from .llm_analyzer import LLMAnalyzer


class ReportGenerator:
    """Generates comprehensive inventory reports combining algorithmic and LLM insights"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.consumption_analyzer = ConsumptionAnalyzer()
        self.llm_analyzer = LLMAnalyzer()
    
    def generate_comprehensive_report(self, restaurant_key: str, 
                                    llm_insights: Optional[LLMInsights] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive inventory report
        
        Args:
            restaurant_key: Restaurant identifier
            llm_insights: Optional pre-generated LLM insights
            
        Returns:
            Complete inventory report dictionary
        """
        try:
            # Get current inventory
            from src.core.ingredient_manager import IngredientManager
            ingredient_manager = IngredientManager(restaurant_key)
            inventory = ingredient_manager.get_inventory()
            
            # Get consumption analysis
            consumption_data = self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
            
            # Get low stock warnings
            warnings = self.consumption_analyzer.get_low_stock_warnings(restaurant_key)
            
            # Get menu data
            from src.core.order_manager import OrderManager
            order_manager = OrderManager(restaurant_key, None, ingredient_manager)
            menu_data = order_manager.get_menu()
            
            # Generate LLM insights if not provided
            if llm_insights is None:
                inventory_data = {
                    'inventory': inventory,
                    'warnings': warnings
                }
                llm_insights = self.llm_analyzer.generate_llm_insights(
                    consumption_data, inventory_data, menu_data
                )
            
            # Format warnings as StockWarning objects
            formatted_warnings = self._format_warnings(warnings)
            
            # Generate report metadata
            metadata = {
                'generated_at': datetime.now().isoformat(),
                'restaurant_key': restaurant_key,
                'total_ingredients': len(inventory),
                'total_warnings': len(warnings),
                'analysis_period_days': consumption_data.get('analysis_period_days', 0),
                'total_tickets_analyzed': consumption_data.get('total_tickets_analyzed', 0)
            }
            
            # Generate consumption analysis summary
            consumption_summary = self._generate_consumption_summary(consumption_data)
            
            # Generate LLM insights summary
            llm_summary = self._generate_llm_summary(llm_insights)
            
            # Create comprehensive report
            report = {
                'metadata': metadata,
                'current_stock': inventory,
                'warnings': [warning.dict() for warning in formatted_warnings],
                'consumption_analysis': consumption_summary,
                'llm_insights': llm_summary,
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            return {
                'error': f"Failed to generate report: {str(e)}",
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'restaurant_key': restaurant_key,
                    'error': True
                }
            }
    
    def _format_warnings(self, warnings: List[Dict[str, Any]]) -> List[StockWarning]:
        """
        Format warnings as StockWarning objects
        
        Args:
            warnings: List of warning dictionaries
            
        Returns:
            List of StockWarning objects
        """
        formatted_warnings = []
        
        for warning in warnings:
            try:
                stock_warning = StockWarning(
                    ingredient_id=warning['ingredient_id'],
                    ingredient_name=warning['ingredient_name'],
                    current_quantity=warning['current_quantity'],
                    unit=warning['unit'],
                    severity=warning['severity'],
                    predicted_runout=datetime.fromisoformat(warning['predicted_runout']),
                    consumption_rate=warning['consumption_rate'],
                    days_remaining=warning['days_remaining'],
                    supplier=warning['supplier'],
                    cost_per_unit=warning['cost_per_unit']
                )
                formatted_warnings.append(stock_warning)
            except Exception as e:
                # Skip malformed warnings
                continue
        
        return formatted_warnings
    
    def _generate_consumption_summary(self, consumption_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate consumption analysis summary
        
        Args:
            consumption_data: Raw consumption analysis data
            
        Returns:
            Formatted consumption summary
        """
        if 'error' in consumption_data:
            return {'error': consumption_data['error']}
        
        per_ingredient = consumption_data.get('per_ingredient', {})
        
        # Calculate overall statistics
        total_ingredients = len(per_ingredient)
        total_usage = sum(data.get('total_usage', 0) for data in per_ingredient.values())
        avg_daily_usage = sum(data.get('avg_daily_usage', 0) for data in per_ingredient.values())
        
        # Find most/least consumed ingredients
        usage_by_ingredient = [
            (ing_id, data.get('total_usage', 0), data.get('avg_daily_usage', 0))
            for ing_id, data in per_ingredient.items()
        ]
        usage_by_ingredient.sort(key=lambda x: x[1], reverse=True)
        
        most_consumed = usage_by_ingredient[:5] if usage_by_ingredient else []
        least_consumed = usage_by_ingredient[-5:] if usage_by_ingredient else []
        
        # Find most volatile ingredients
        volatility_by_ingredient = [
            (ing_id, data.get('usage_volatility', 0))
            for ing_id, data in per_ingredient.items()
        ]
        volatility_by_ingredient.sort(key=lambda x: x[1], reverse=True)
        most_volatile = volatility_by_ingredient[:5] if volatility_by_ingredient else []
        
        return {
            'total_ingredients_analyzed': total_ingredients,
            'total_usage_analyzed': total_usage,
            'average_daily_usage': avg_daily_usage,
            'most_consumed_ingredients': most_consumed,
            'least_consumed_ingredients': least_consumed,
            'most_volatile_ingredients': most_volatile,
            'analysis_period_days': consumption_data.get('analysis_period_days', 0),
            'total_tickets_analyzed': consumption_data.get('total_tickets_analyzed', 0),
            'per_ingredient_details': per_ingredient
        }
    
    def _generate_llm_summary(self, llm_insights: LLMInsights) -> Dict[str, Any]:
        """
        Generate LLM insights summary
        
        Args:
            llm_insights: LLM insights object
            
        Returns:
            Formatted LLM summary
        """
        return {
            'reorder_suggestions': [
                {
                    'ingredient_id': suggestion.ingredient_id,
                    'ingredient_name': suggestion.ingredient_name,
                    'suggested_quantity': suggestion.suggested_quantity,
                    'unit': suggestion.unit,
                    'reasoning': suggestion.reasoning,
                    'urgency': suggestion.urgency,
                    'estimated_cost': suggestion.estimated_cost,
                    'supplier': suggestion.supplier,
                    'delivery_time_days': suggestion.delivery_time_days,
                    'storage_considerations': suggestion.storage_considerations
                }
                for suggestion in llm_insights.reorder_suggestions
            ],
            'critical_items': llm_insights.critical_items,
            'optimization_tips': llm_insights.optimization_tips,
            'seasonal_recommendations': llm_insights.seasonal_recommendations,
            'cost_optimization_suggestions': llm_insights.cost_optimization_suggestions,
            'supplier_analysis': llm_insights.supplier_analysis,
            'inventory_turnover_insights': llm_insights.inventory_turnover_insights
        }
    
    def generate_low_stock_alerts(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Generate low stock alerts for immediate action
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of urgent stock alerts
        """
        warnings = self.consumption_analyzer.get_low_stock_warnings(restaurant_key)
        
        # Filter for high and critical severity warnings
        urgent_warnings = [
            warning for warning in warnings 
            if warning['severity'] in ['high', 'critical']
        ]
        
        return urgent_warnings
    
    def generate_reorder_suggestions(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Generate reorder suggestions based on consumption patterns
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of reorder suggestions
        """
        # Get consumption data
        consumption_data = self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
        
        # Get current inventory
        from src.core.ingredient_manager import IngredientManager
        ingredient_manager = IngredientManager(restaurant_key)
        inventory = ingredient_manager.get_inventory()
        
        # Get warnings
        warnings = self.consumption_analyzer.get_low_stock_warnings(restaurant_key)
        
        # Generate LLM insights
        inventory_data = {
            'inventory': inventory,
            'warnings': warnings
        }
        
        # Get menu data
        from src.core.order_manager import OrderManager
        order_manager = OrderManager(restaurant_key, None, ingredient_manager)
        menu_data = order_manager.get_menu()
        
        llm_insights = self.llm_analyzer.generate_llm_insights(
            consumption_data, inventory_data, menu_data
        )
        
        # Format reorder suggestions
        suggestions = []
        for suggestion in llm_insights.reorder_suggestions:
            suggestions.append({
                'ingredient_id': suggestion.ingredient_id,
                'ingredient_name': suggestion.ingredient_name,
                'suggested_quantity': suggestion.suggested_quantity,
                'unit': suggestion.unit,
                'reasoning': suggestion.reasoning,
                'urgency': suggestion.urgency,
                'estimated_cost': suggestion.estimated_cost,
                'supplier': suggestion.supplier,
                'delivery_time_days': suggestion.delivery_time_days,
                'storage_considerations': suggestion.storage_considerations
            })
        
        return suggestions
    
    def export_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """
        Export report to JSON file
        
        Args:
            report: Report dictionary
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
