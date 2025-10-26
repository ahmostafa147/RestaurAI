import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mcp.server.fastmcp import FastMCP
# from mcp.server.http import HTTPServer
import json
from src.core.restaurant import Restaurant

# Initialize FastMCP server
mcp = FastMCP("restaurant-mcp", port = 8001)

@mcp.tool()
def create_restaurant(name: str) -> str:
    """Create new restaurant and return access key."""
    try:
        r = Restaurant(name=name)
        return json.dumps({"name": r.name, "key": r.key})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_menu(key: str) -> str:
    """Get restaurant menu."""
    try:
        r = Restaurant(key=key)
        return json.dumps(r.get_menu(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def reserve_table(key: str, name: str, party_size: int, time: str) -> str:
    """Make a table reservation."""
    try:
        r = Restaurant(key=key)
        result = r.reserve_table(name, party_size, time)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def place_order(key: str, table_number: int, item_ids: list[int]) -> str:
    """Place an order for a table."""
    try:
        r = Restaurant(key=key)
        result = r.place_order(table_number, item_ids)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def seat_party(key: str, table_number: int) -> str:
    """Seat party at table."""
    try:
        r = Restaurant(key=key)
        r.seat_party(table_number)
        return json.dumps({"status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def clear_table(key: str, table_number: int) -> str:
    """Clear table after party leaves."""
    try:
        r = Restaurant(key=key)
        r.clear_table(table_number)
        return json.dumps({"status": "success"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_reservations(key: str) -> str:
    """Get all reservations for restaurant."""
    try:
        r = Restaurant(key=key)
        result = r.get_reservations()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_orders(key: str) -> str:
    """Get all orders for restaurant."""
    try:
        r = Restaurant(key=key)
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
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from menu_agent.src.menu_agent import MenuAgent
        
        # Initialize menu agent
        menu_agent = MenuAgent()
        
        # Generate analytics report
        report = menu_agent.generate_analytics_report(key, review_analytics_path)
        
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    mcp.run(transport="sse")
