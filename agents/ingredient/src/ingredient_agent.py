"""
Main orchestrator for ingredient agent analytics
"""

import sys
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .analytics.consumption_analyzer import ConsumptionAnalyzer
from .analytics.llm_analyzer import LLMAnalyzer
from .analytics.report_generator import ReportGenerator
from .analytics.models import LLMInsights


class IngredientAgent:
    """Main orchestrator for ingredient analytics and inventory management"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the ingredient agent with analyzers
        
        Args:
            anthropic_api_key: Anthropic API key for LLM analysis
        """
        self.consumption_analyzer = ConsumptionAnalyzer()
        self.llm_analyzer = LLMAnalyzer(anthropic_api_key)
        self.report_generator = ReportGenerator()
        self.restaurants = self._load_restaurants()
    
    def _load_restaurants(self) -> List[Dict[str, Any]]:
        """Load restaurant configurations from unified restaurants.json"""
        restaurants_file = os.path.join(os.path.dirname(__file__), '..', '..', 'restaurants.json')
        if os.path.exists(restaurants_file):
            with open(restaurants_file, 'r') as f:
                config = json.load(f)
                return config.get('restaurants', [])
        return []
    
    def load_report(self, secure_key: str) -> Optional[Dict[str, Any]]:
        """
        Load a report for a restaurant by secure_key.
        If no report exists, generates a new one.
        
        Args:
            secure_key: Restaurant secure key
            
        Returns:
            Report dictionary or None if generation fails
        """
        # Look for existing report files in data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        
        # Try to find the most recent report for this restaurant
        # Reports are saved with pattern: {secure_key}_{timestamp}.json
        report_files = []
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.startswith(secure_key) and filename.endswith('.json'):
                    file_path = os.path.join(data_dir, filename)
                    try:
                        stat = os.stat(file_path)
                        report_files.append({
                            'path': file_path,
                            'time': stat.st_mtime
                        })
                    except:
                        continue
        
        # If we found existing reports, return the most recent one
        if report_files:
            latest = max(report_files, key=lambda x: x['time'])
            try:
                with open(latest['path'], 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading report from {latest['path']}: {e}")
        
        # If no report found, generate a new one
        print(f"No existing report found for {secure_key}, generating new report...")
        return self.generate_inventory_report(secure_key)
    def generate_inventory_report(self, restaurant_key: str, 
                                output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive inventory analytics report
        
        Args:
            restaurant_key: Restaurant identifier
            output_path: Optional path to save report as JSON file
            
        Returns:
            Complete inventory report dictionary
        """
        try:
            # Generate the comprehensive report
            report = self.report_generator.generate_comprehensive_report(restaurant_key)
            
            # Save to file if output path provided
            if output_path and 'error' not in report:
                success = self.report_generator.export_report(report, output_path)
                if success:
                    report['metadata']['saved_to'] = output_path
            
            return report
            
        except Exception as e:
            return {
                'error': f"Failed to generate inventory report: {str(e)}",
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'restaurant_key': restaurant_key,
                    'error': True
                }
            }
    
    def generate_multi_restaurant_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate analytics report for all configured restaurants"""
        restaurants_report = {}
        
        for restaurant in self.restaurants:
            restaurant_id = restaurant['id']
            restaurant_name = restaurant['name']
            secure_key = restaurant['secure_key']
            
            try:
                # Generate analytics for this restaurant
                analytics = self.generate_inventory_report(secure_key)
                
                restaurants_report[restaurant_id] = {
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "analytics": analytics
                }
            except Exception as e:
                restaurants_report[restaurant_id] = {
                    "id": restaurant_id,
                    "name": restaurant_name,
                    "error": f"Failed to generate analytics: {str(e)}"
                }
        
        # Save multi-restaurant report if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "restaurants": restaurants_report
                }, f, indent=2)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "restaurants": restaurants_report
        }
    
    def get_low_stock_alerts(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Get immediate low stock warnings for ingredients predicted to run out soon
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of urgent stock alerts
        """
        try:
            return self.report_generator.generate_low_stock_alerts(restaurant_key)
        except Exception as e:
            return [{'error': f"Failed to get low stock alerts: {str(e)}"}]
    
    def get_reorder_suggestions(self, restaurant_key: str) -> List[Dict[str, Any]]:
        """
        Get LLM-powered reorder suggestions based on consumption patterns
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            List of reorder suggestions with quantities and reasoning
        """
        try:
            return self.report_generator.generate_reorder_suggestions(restaurant_key)
        except Exception as e:
            return [{'error': f"Failed to get reorder suggestions: {str(e)}"}]
    
    def analyze_consumption_patterns(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Analyze historical consumption patterns for ingredients
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Consumption analysis data
        """
        try:
            return self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
        except Exception as e:
            return {'error': f"Failed to analyze consumption patterns: {str(e)}"}
    
    def predict_stockout_time(self, restaurant_key: str, ingredient_id: int) -> Dict[str, Any]:
        """
        Predict when a specific ingredient will run out
        
        Args:
            restaurant_key: Restaurant identifier
            ingredient_id: Ingredient to analyze
            
        Returns:
            Stockout prediction data
        """
        try:
            # Get current inventory
            from backend.src.core.ingredient_manager import IngredientManager
            ingredient_manager = IngredientManager(restaurant_key)
            ingredient = ingredient_manager.get_ingredient(ingredient_id)
            
            if not ingredient:
                return {'error': f'Ingredient {ingredient_id} not found'}
            
            # Get consumption data
            consumption_data = self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
            ingredient_id_str = str(ingredient_id)
            
            if ingredient_id_str not in consumption_data.get('per_ingredient', {}):
                return {'error': f'No consumption data for ingredient {ingredient_id}'}
            
            consumption_info = consumption_data['per_ingredient'][ingredient_id_str]
            avg_hourly_usage = consumption_info['avg_hourly_usage']
            
            # Predict stockout time
            predicted_stockout = self.consumption_analyzer.predict_stockout_time(
                ingredient_id, ingredient.quantity, avg_hourly_usage, ingredient.unit
            )
            
            return {
                'ingredient_id': ingredient_id,
                'ingredient_name': ingredient.name,
                'current_quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'avg_hourly_usage': avg_hourly_usage,
                'predicted_stockout': predicted_stockout.isoformat(),
                'hours_remaining': (predicted_stockout - datetime.now()).total_seconds() / 3600,
                'days_remaining': (predicted_stockout - datetime.now()).total_seconds() / (3600 * 24)
            }
            
        except Exception as e:
            return {'error': f"Failed to predict stockout time: {str(e)}"}
    
    def get_available_reports(self) -> List[str]:
        """
        Get list of available inventory reports
        
        Returns:
            List of report file paths
        """
        try:
            import glob
            report_pattern = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'inventory_report*.json')
            reports = glob.glob(report_pattern)
            return [os.path.basename(report) for report in reports]
        except Exception as e:
            return []
    
    def get_ingredient_usage_summary(self, restaurant_key: str) -> Dict[str, Any]:
        """
        Get summary of ingredient usage patterns
        
        Args:
            restaurant_key: Restaurant identifier
            
        Returns:
            Usage summary data
        """
        try:
            consumption_data = self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
            
            if 'error' in consumption_data:
                return consumption_data
            
            per_ingredient = consumption_data.get('per_ingredient', {})
            
            # Calculate summary statistics
            total_ingredients = len(per_ingredient)
            total_usage = sum(data.get('total_usage', 0) for data in per_ingredient.values())
            avg_daily_usage = sum(data.get('avg_daily_usage', 0) for data in per_ingredient.values())
            
            # Find top consumers
            usage_by_ingredient = [
                (ing_id, data.get('total_usage', 0), data.get('avg_daily_usage', 0))
                for ing_id, data in per_ingredient.items()
            ]
            usage_by_ingredient.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'total_ingredients_analyzed': total_ingredients,
                'total_usage_analyzed': total_usage,
                'average_daily_usage': avg_daily_usage,
                'top_consumed_ingredients': usage_by_ingredient[:10],
                'analysis_period_days': consumption_data.get('analysis_period_days', 0),
                'total_tickets_analyzed': consumption_data.get('total_tickets_analyzed', 0)
            }
            
        except Exception as e:
            return {'error': f"Failed to get usage summary: {str(e)}"}
    
    def check_ingredient_availability(self, restaurant_key: str, ingredient_name: str) -> Dict[str, Any]:
        """
        Check availability and stock status of a specific ingredient
        
        Args:
            restaurant_key: Restaurant identifier
            ingredient_name: Name of ingredient to check
            
        Returns:
            Ingredient availability data
        """
        try:
            from backend.src.core.ingredient_manager import IngredientManager
            ingredient_manager = IngredientManager(restaurant_key)
            ingredient = ingredient_manager.get_ingredient_by_name(ingredient_name)
            
            if not ingredient:
                return {'error': f'Ingredient "{ingredient_name}" not found'}
            
            # Get consumption data
            consumption_data = self.consumption_analyzer.analyze_consumption_patterns(restaurant_key)
            ingredient_id_str = str(ingredient.id)
            
            consumption_info = consumption_data.get('per_ingredient', {}).get(ingredient_id_str, {})
            
            # Check if it's in low stock warnings
            warnings = self.consumption_analyzer.get_low_stock_warnings(restaurant_key)
            is_low_stock = any(w['ingredient_id'] == ingredient.id for w in warnings)
            
            return {
                'ingredient_id': ingredient.id,
                'ingredient_name': ingredient.name,
                'current_quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'available': ingredient.available,
                'cost_per_unit': ingredient.cost,
                'supplier': ingredient.supplier,
                'is_low_stock': is_low_stock,
                'avg_daily_usage': consumption_info.get('avg_daily_usage', 0),
                'avg_hourly_usage': consumption_info.get('avg_hourly_usage', 0),
                'usage_volatility': consumption_info.get('usage_volatility', 0),
                'menu_items': consumption_info.get('menu_items', [])
            }
            
        except Exception as e:
            return {'error': f"Failed to check ingredient availability: {str(e)}"}
