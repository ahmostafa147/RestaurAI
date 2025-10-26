import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mcp.server.fastmcp import FastMCP
# from mcp.server.http import HTTPServer
import json
from src.core.restaurant import Restaurant
from src.utils.restaurant_auth import get_auth_instance

# Initialize FastMCP server
mcp = FastMCP("restaurant-mcp", port = 8001)

# Initialize authentication
auth = get_auth_instance()

@mcp.tool()
def get_restaurants() -> str:
    """Get list of all available restaurants."""
    try:
        restaurants = auth.get_all_restaurants()
        print("get_restaurants in use")
        
        return json.dumps({"restaurants": restaurants})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def authenticate_restaurant(restaurant_name: str, password: str = "") -> str:
    """Authenticate restaurant and get secure key."""
    try:
        key = auth.validate_credentials(restaurant_name, password)
        print("authenticate_restaurant in use")
        
        if key:
            return json.dumps({
                "success": True,
                "restaurant_name": restaurant_name,
                "secure_key": key
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Invalid restaurant name"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def create_restaurant(name: str) -> str:
    """Create new restaurant and return access key."""
    try:
        r = Restaurant(name=name)
        print("create_restaurant in use")
        
        return json.dumps({"name": r.name, "key": r.key})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_menu(key: str) -> str:
    """Get restaurant menu."""
    try:
        r = Restaurant(key=key)
        print("get_menu in use")
        
        return json.dumps(r.get_menu(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def reserve_table(key: str, name: str, party_size: int, time: str) -> str:
    """Make a table reservation."""
    try:
        r = Restaurant(key=key)
        print("reserve_table in use")
        
        result = r.reserve_table(name, party_size, time)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def place_order(key: str, table_number: int, item_ids: list[int]) -> str:
    """Place an order for a table."""
    try:
        r = Restaurant(key=key)
        print("place_order in use")
        
        result = r.place_order(table_number, item_ids)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def seat_party(key: str, table_number: int) -> str:
    """Seat party at table."""
    try:
        r = Restaurant(key=key)
        print("seat_party in use")
        
        r.seat_party(table_number)
        return json.dumps({"status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def clear_table(key: str, table_number: int) -> str:
    """Clear table after party leaves."""
    try:
        r = Restaurant(key=key)
        print("clear_table in use")
        
        r.clear_table(table_number)
        return json.dumps({"status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_reservations(key: str) -> str:
    """Get all reservations for restaurant."""
    try:
        r = Restaurant(key=key)
        print("get_reservations in use")
        
        result = r.get_reservations()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_orders(key: str) -> str:
    """Get all orders for restaurant."""
    try:
        r = Restaurant(key=key)
        print("get_orders in use")
        
        result = r.get_orders()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def generate_menu_analytics(key: str, review_analytics_path: str = None) -> str:
    """Generate comprehensive menu analytics report."""
    try:
        # Import MenuAgent here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from agents.menu.src.menu_agent import MenuAgent
        
        # Initialize menu agent
        menu_agent = MenuAgent()
        print("generate_menu_analytics in use")
        
        # Generate analytics report
        report = menu_agent.generate_analytics_report(key, review_analytics_path)
        
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def generate_inventory_report(key: str) -> str:
    """Generate comprehensive inventory analytics report."""
    try:
        # Import IngredientAgent here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from agents.ingredient.src.ingredient_agent import IngredientAgent
        
        # Initialize ingredient agent
        ingredient_agent = IngredientAgent()
        print("generate_inventory_report in use")
        # Generate inventory report
        report = ingredient_agent.generate_inventory_report(key)
        
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_low_stock_alerts(key: str) -> str:
    """Get immediate low stock warnings for ingredients predicted to run out soon."""
    try:
        # Import IngredientAgent here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from agents.ingredient.src.ingredient_agent import IngredientAgent
        
        # Initialize ingredient agent
        ingredient_agent = IngredientAgent()
        print("get_low_stock_alerts in use")
        
        # Get low stock alerts
        alerts = ingredient_agent.get_low_stock_alerts(key)
        
        return json.dumps(alerts, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_reorder_suggestions(key: str) -> str:
    """Get LLM-powered reorder suggestions based on consumption patterns."""
    try:
        # Import IngredientAgent here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from agents.ingredient.src.ingredient_agent import IngredientAgent
        print("get_reorder_suggestions in use")
        # Initialize ingredient agent
        ingredient_agent = IngredientAgent()
        
        # Get reorder suggestions
        suggestions = ingredient_agent.get_reorder_suggestions(key)
        
        return json.dumps(suggestions, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    print("Starting Restaurant MCP Server...")
    print("Server running on http://127.0.0.1:8001")
    print("Transport: SSE")
    mcp.run(transport="sse")
