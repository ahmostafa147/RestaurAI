import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from backend.src.database import db
from backend.src.core.restaurant import Restaurant

from .analytics.menu_analyzer import MenuAnalyzer
from .analytics.llm_analyzer import LLMAnalyzer
from .analytics.report_generator import ReportGenerator
from .analytics.models import LLMInsights


class MenuAgent:
    """Main orchestrator for menu analytics"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize the menu agent with analyzers"""
        self.menu_analyzer = MenuAnalyzer()
        self.llm_analyzer = LLMAnalyzer(anthropic_api_key)
        self.report_generator = ReportGenerator()

        # Create reports directory in project data folder
        project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        self.reports_dir = os.path.join(project_root, 'data', 'menu_reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_analytics_report(
        self, 
        restaurant_key: str, 
        review_analytics_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive menu analytics report"""
        
        try:
            # Load restaurant data
            restaurant = Restaurant(key=restaurant_key)
            menu_data = restaurant.get_menu_dict()
            
            # Get all menu items for analysis
            all_menu_items = []
            for category, items in menu_data.items():
                for item_dict in items:
                    # Convert dict back to MenuItem object for analysis
                    from backend.src.models.menu import MenuItem
                    from backend.src.models.ingredient import Ingredient
                    
                    ingredients = []
                    for ing_dict in item_dict.get('ingredients', []):
                        ingredient = Ingredient(
                            id=ing_dict['id'],
                            name=ing_dict['name'],
                            quantity=ing_dict['quantity'],
                            unit=ing_dict['unit'],
                            available=ing_dict.get('available', True),
                            cost=ing_dict.get('cost', 0.0),
                            supplier=ing_dict.get('supplier', '')
                        )
                        ingredients.append(ingredient)
                    
                    menu_item = MenuItem(
                        id=item_dict['id'],
                        name=item_dict['name'],
                        price=item_dict['price'],
                        category=category,
                        description=item_dict.get('description'),
                        available=item_dict.get('available', True),
                        ingredients=ingredients
                    )
                    all_menu_items.append(menu_item)
            
            # Load historical ticket data
            closed_tickets = self._load_closed_tickets(restaurant_key)
            
            # Load review analytics if provided
            review_analytics = None
            if review_analytics_path and os.path.exists(review_analytics_path):
                with open(review_analytics_path, 'r') as f:
                    review_analytics = json.load(f)
            
            # Run algorithmic analysis
            algorithmic_results = self.menu_analyzer.analyze_menu_performance(
                closed_tickets, all_menu_items
            )
            
            # Run LLM analysis
            llm_insights = self.llm_analyzer.generate_llm_insights(
                menu_data, review_analytics, algorithmic_results
            )
            
            # Generate comprehensive report
            report = self.report_generator.generate_comprehensive_report(
                restaurant_key, menu_data, algorithmic_results, 
                llm_insights, review_analytics
            )
            
            # Save report to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"{restaurant_key}_{timestamp}.json"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Add report path to metadata
            report['metadata']['report_file'] = report_path
            
            return report
            
        except Exception as e:
            return {
                'error': f"Failed to generate analytics report: {str(e)}",
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'restaurant_key': restaurant_key,
                    'status': 'error'
                }
            }
    
    def _load_closed_tickets(self, restaurant_key: str) -> List[Dict]:
        """Load closed tickets from database"""
        try:
            events = db.get_events(restaurant_key, "closed_ticket")
            return [event['data'] for event in events]
        except Exception as e:
            print(f"Warning: Could not load closed tickets: {e}")
            return []
    
    def get_available_reports(self) -> List[Dict[str, str]]:
        """Get list of available report files"""
        reports = []
        if os.path.exists(self.reports_dir):
            for filename in os.listdir(self.reports_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.reports_dir, filename)
                    stat = os.stat(file_path)
                    reports.append({
                        'filename': filename,
                        'path': file_path,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'size_bytes': stat.st_size
                    })
        return sorted(reports, key=lambda x: x['created_at'], reverse=True)
    
    def load_report(self, report_path: str) -> Dict[str, Any]:
        """Load a specific report from file"""
        try:
            with open(report_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'error': f"Failed to load report: {str(e)}"}
    
    def get_report_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the report"""
        metadata = report.get('metadata', {})
        summary_metrics = report.get('summary_metrics', {})
        
        return {
            'restaurant_key': metadata.get('restaurant_key'),
            'generated_at': metadata.get('generated_at'),
            'total_menu_items': summary_metrics.get('total_menu_items', 0),
            'total_orders': summary_metrics.get('total_orders', 0),
            'total_revenue': summary_metrics.get('total_revenue', 0),
            'average_order_value': summary_metrics.get('average_order_value', 0),
            'average_profit_margin': summary_metrics.get('average_profit_margin', 0),
            'most_popular_item': summary_metrics.get('most_popular_item', {}),
            'highest_profit_item': summary_metrics.get('highest_profit_item', {}),
            'busiest_hour': summary_metrics.get('busiest_hour'),
            'busiest_day': summary_metrics.get('busiest_day')
        }
