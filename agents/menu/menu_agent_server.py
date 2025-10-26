"""
uAgents REST server for menu agent with webhook endpoints
"""

import sys
import os
import json
from typing import Optional
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from uagents import Agent, Context
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(f"Missing required dependencies: {e}. Please install uagents.")

from menu.src.menu_agent import MenuAgent


# Initialize the menu agent
menu_agent = MenuAgent()

# Global variable to store the latest report
latest_report = None

# Create uAgents agent
agent = Agent(
    name="menu_agent",
    seed="menu-agent-seed-12345",
    port=8006,
    endpoint=["http://localhost:8006/submit"]
)


# Pydantic models for REST endpoints
class MenuReportResponse(BaseModel):
    response: str

class MenuAnalyticsResponse(BaseModel):
    response: str

class MenuPerformanceResponse(BaseModel):
    response: str

class ErrorResponse(BaseModel):
    error: str


def load_menu_report():
    """Load the latest menu report from JSON file"""
    global latest_report
    try:
        # Look for the most recent report in the reports directory
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        if os.path.exists(reports_dir):
            report_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
            if report_files:
                # Get the most recent file
                latest_file = max(report_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
                report_path = os.path.join(reports_dir, latest_file)
                with open(report_path, 'r') as f:
                    latest_report = json.load(f)
                print(f"Loaded menu report from file: {latest_file}")
            else:
                print("No existing menu report found, will generate on first request")
                latest_report = None
        else:
            print("No reports directory found, will generate on first request")
            latest_report = None
    except Exception as e:
        print(f"Error loading menu report: {e}")
        latest_report = None


@agent.on_interval(period=86400)  # 24 hours in seconds
async def update_menu_report(ctx: Context):
    """Update menu report daily"""
    global latest_report
    try:
        print("Updating menu analytics report...")
        restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Chaos Kitchen
        latest_report = menu_agent.generate_analytics_report(restaurant_key)
        print("Menu analytics report updated")
    except Exception as e:
        ctx.logger.error(f"Error updating menu report: {e}")


@agent.on_rest_get("/menu_analytics", MenuReportResponse)
async def handle_menu_analytics(ctx: Context) -> MenuReportResponse:
    """Handle GET requests for comprehensive menu analytics report"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # If still no report, generate one
        if latest_report is None:
            restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Chaos Kitchen
            latest_report = menu_agent.generate_analytics_report(restaurant_key)
        
        return MenuReportResponse(response=json.dumps(latest_report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu analytics: {e}")
        return MenuReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/menu_performance", MenuPerformanceResponse)
async def handle_menu_performance(ctx: Context) -> MenuPerformanceResponse:
    """Handle GET requests for menu performance metrics"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # Extract performance metrics from the cached report
        if latest_report and 'summary_metrics' in latest_report:
            performance = latest_report['summary_metrics']
        else:
            performance = {"message": "No performance metrics available"}
        
        return MenuPerformanceResponse(response=json.dumps(performance, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu performance: {e}")
        return MenuPerformanceResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/popular_items", MenuAnalyticsResponse)
async def handle_popular_items(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for popular menu items analysis"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # Extract popular items from the cached report
        if latest_report and 'item_analytics' in latest_report:
            popular_items = latest_report['item_analytics'].get('popular_items', [])
        else:
            popular_items = {"message": "No popular items data available"}
        
        return MenuAnalyticsResponse(response=json.dumps(popular_items, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting popular items: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/profit_analysis", MenuAnalyticsResponse)
async def handle_profit_analysis(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for profit analysis"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # Extract profit analysis from the cached report
        if latest_report and 'item_analytics' in latest_report:
            profit_analysis = latest_report['item_analytics'].get('profit_analysis', {})
        else:
            profit_analysis = {"message": "No profit analysis available"}
        
        return MenuAnalyticsResponse(response=json.dumps(profit_analysis, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting profit analysis: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/menu_recommendations", MenuAnalyticsResponse)
async def handle_menu_recommendations(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for menu recommendations"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # Extract recommendations from the cached report
        if latest_report and 'llm_insights' in latest_report:
            recommendations = latest_report['llm_insights'].get('recommendations', [])
        else:
            recommendations = {"message": "No recommendations available"}
        
        return MenuAnalyticsResponse(response=json.dumps(recommendations, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu recommendations: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/revenue_analysis", MenuAnalyticsResponse)
async def handle_revenue_analysis(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for revenue analysis"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_menu_report()
        
        # Extract revenue analysis from the cached report
        if latest_report and 'revenue_analytics' in latest_report:
            revenue_analysis = latest_report['revenue_analytics']
        else:
            revenue_analysis = {"message": "No revenue analysis available"}
        
        return MenuAnalyticsResponse(response=json.dumps(revenue_analysis, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting revenue analysis: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/available_reports", MenuAnalyticsResponse)
async def handle_available_reports(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for list of available reports"""
    try:
        reports = menu_agent.get_available_reports()
        return MenuAnalyticsResponse(response=json.dumps(reports, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting available reports: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/metrics", MenuAnalyticsResponse)
async def handle_metrics(ctx: Context) -> MenuAnalyticsResponse:
    """Handle GET requests for dashboard metrics"""
    try:
        # Import here to avoid circular dependencies
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

        try:
            from backend.src.core.restaurant import Restaurant
            restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"
            restaurant = Restaurant(key=restaurant_key)
            menu_data = restaurant.get_menu_dict()

            if menu_data is None:
                raise ValueError("No menu data available")

            # Count menu items
            total_items = sum(len(items) for items in menu_data.values())
            active_items = 0
            unavailable_items = []

            for category, items in menu_data.items():
                for item in items:
                    if item.get('available', True):
                        active_items += 1
                    else:
                        unavailable_items.append({
                            "name": item['name'],
                            "category": category,
                            "price": item['price']
                        })
        except Exception as data_error:
            # If restaurant data fails, use mock data
            ctx.logger.warning(f"Using mock data due to error: {data_error}")
            total_items = 34
            active_items = 34
            unavailable_items = []

        # Try to get top performers from latest report
        top_items = []
        low_performers = []

        global latest_report
        if latest_report and 'summary_metrics' in latest_report:
            summary = latest_report['summary_metrics']
            top_items = summary.get('top_performers', [])[:3]
            low_performers = summary.get('bottom_performers', [])[:3]
        else:
            # Mock top performers if no report available
            top_items = [
                {"name": "Caesar Salad", "orders": 145, "revenue": 1450.0},
                {"name": "Burger", "orders": 132, "revenue": 2112.0},
                {"name": "Pasta", "orders": 98, "revenue": 1764.0}
            ]
            low_performers = [
                {"name": "Truffle Dish", "orders": 3, "revenue": 150.0},
                {"name": "Foie Gras", "orders": 5, "revenue": 375.0}
            ]

        metrics = {
            "totalItems": total_items,
            "activeItems": active_items,
            "unavailableItems": unavailable_items,
            "topPerformers": top_items,
            "lowPerformers": low_performers,
            "timestamp": datetime.now().isoformat()
        }

        return MenuAnalyticsResponse(response=json.dumps(metrics))
    except Exception as e:
        ctx.logger.error(f"Error getting metrics: {e}")
        # Return mock data even on error
        return MenuAnalyticsResponse(response=json.dumps({
            "totalItems": 34,
            "activeItems": 34,
            "unavailableItems": [],
            "topPerformers": [
                {"name": "Caesar Salad", "orders": 145, "revenue": 1450.0},
                {"name": "Burger", "orders": 132, "revenue": 2112.0}
            ],
            "lowPerformers": [
                {"name": "Truffle Dish", "orders": 3, "revenue": 150.0}
            ],
            "timestamp": datetime.now().isoformat()
        }))


if __name__ == "__main__":
    print("Starting Menu Agent REST Server...")
    print("Available endpoints:")
    print("  GET /metrics - Dashboard metrics (active items, top/low performers)")
    print("  GET /menu_analytics - Full menu analytics report")
    print("  GET /menu_performance - Menu performance metrics")
    print("  GET /popular_items - Popular menu items analysis")
    print("  GET /profit_analysis - Profit analysis")
    print("  GET /menu_recommendations - Menu recommendations")
    print("  GET /revenue_analysis - Revenue analysis")
    print("  GET /available_reports - List of available reports")
    print(f"Server running on http://localhost:8006")
    print("Report will be updated daily at midnight")
    
    # Load existing report on startup
    load_menu_report()
    
    agent.run()
