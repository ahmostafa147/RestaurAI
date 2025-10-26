"""
uAgents REST server for ingredient agent with webhook endpoints
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

from ingredient_agent.src.ingredient_agent import IngredientAgent


# Initialize the ingredient agent
ingredient_agent = IngredientAgent()

# Global variable to store the latest report
latest_report = None

# Create uAgents agent
agent = Agent(
    name="ingredient_agent_v2",
    seed="ingredient-agent-seed-12345-v2",
    port=8005,
    endpoint=["http://localhost:8004/submit"]
)


# Pydantic models for REST endpoints
class InventoryReportResponse(BaseModel):
    response: str

class LowStockResponse(BaseModel):
    response: str

class ReorderSuggestionsResponse(BaseModel):
    response: str

class ErrorResponse(BaseModel):
    error: str


def load_inventory_report():
    """Load the latest inventory report from JSON file"""
    global latest_report
    try:
        with open('inventory_report.json', 'r') as f:
            latest_report = json.load(f)
        print(f"Loaded inventory report from file")
    except FileNotFoundError:
        print("No existing inventory report found, will generate on first request")
        latest_report = None
    except Exception as e:
        print(f"Error loading inventory report: {e}")
        latest_report = None


@agent.on_interval(period=86400)  # 24 hours in seconds
async def update_inventory_report(ctx: Context):
    """Update inventory report daily"""
    global latest_report
    try:
        print("Updating inventory report...")
        restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Chaos Kitchen
        latest_report = ingredient_agent.generate_inventory_report(restaurant_key)
        
        # Save to file
        with open('inventory_report.json', 'w') as f:
            json.dump(latest_report, f, indent=2)
        print("Inventory report updated and saved")
    except Exception as e:
        ctx.logger.error(f"Error updating inventory report: {e}")


@agent.on_rest_get("/inventory_report", InventoryReportResponse)
async def handle_inventory_report(ctx: Context) -> InventoryReportResponse:
    """Handle GET requests for comprehensive inventory report"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # If still no report, generate one
        if latest_report is None:
            restaurant_key = "113b9b80-dda7-41e1-b6d1-f1d7428950c3"  # Chaos Kitchen
            latest_report = ingredient_agent.generate_inventory_report(restaurant_key)
            # Save it
            with open('inventory_report.json', 'w') as f:
                json.dump(latest_report, f, indent=2)
        
        return InventoryReportResponse(response=json.dumps(latest_report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting inventory report: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/low_stock", LowStockResponse)
async def handle_low_stock_alerts(ctx: Context) -> LowStockResponse:
    """Handle GET requests for low stock alerts"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # Extract low stock alerts from the cached report
        if latest_report and 'low_stock_alerts' in latest_report:
            alerts = latest_report['low_stock_alerts']
        else:
            alerts = []
        
        return LowStockResponse(response=json.dumps(alerts, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting low stock alerts: {e}")
        return LowStockResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/reorder_suggestions", ReorderSuggestionsResponse)
async def handle_reorder_suggestions(ctx: Context) -> ReorderSuggestionsResponse:
    """Handle GET requests for reorder suggestions"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # Extract reorder suggestions from the cached report
        if latest_report and 'reorder_suggestions' in latest_report:
            suggestions = latest_report['reorder_suggestions']
        else:
            suggestions = []
        
        return ReorderSuggestionsResponse(response=json.dumps(suggestions, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting reorder suggestions: {e}")
        return ReorderSuggestionsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/consumption_analysis", InventoryReportResponse)
async def handle_consumption_analysis(ctx: Context) -> InventoryReportResponse:
    """Handle GET requests for consumption pattern analysis"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # Extract consumption analysis from the cached report
        if latest_report and 'consumption_analysis' in latest_report:
            analysis = latest_report['consumption_analysis']
        else:
            analysis = {"message": "No consumption analysis available"}
        
        return InventoryReportResponse(response=json.dumps(analysis, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting consumption analysis: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/ingredient_status", InventoryReportResponse)
async def handle_ingredient_status(ctx: Context) -> InventoryReportResponse:
    """Handle GET requests for specific ingredient status"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # For now, return a simple message since we don't have specific ingredient lookup
        # In a real implementation, you'd search through the inventory data
        status = {"message": "Ingredient status lookup not implemented in cached mode"}
        
        return InventoryReportResponse(response=json.dumps(status, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error checking ingredient status: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/usage_summary", InventoryReportResponse)
async def handle_usage_summary(ctx: Context) -> InventoryReportResponse:
    """Handle GET requests for ingredient usage summary"""
    try:
        global latest_report
        
        # If no report loaded, try to load from file
        if latest_report is None:
            load_inventory_report()
        
        # Extract usage summary from the cached report
        if latest_report and 'usage_summary' in latest_report:
            summary = latest_report['usage_summary']
        else:
            summary = {"message": "No usage summary available"}
        
        return InventoryReportResponse(response=json.dumps(summary, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting usage summary: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


if __name__ == "__main__":
    print("Starting Ingredient Agent REST Server...")
    print("Available endpoints:")
    print("  GET /inventory_report - Full inventory report (cached)")
    print("  GET /low_stock - Low stock alerts")
    print("  GET /reorder_suggestions - Reorder suggestions")
    print("  GET /consumption_analysis - Consumption analysis")
    print("  GET /ingredient_status?ingredient=<name> - Ingredient status")
    print("  GET /usage_summary - Usage summary")
    print(f"Server running on port 8004")
    print("Report will be updated daily at midnight")
    
    # Load existing report on startup
    load_inventory_report()
    
    agent.run()
