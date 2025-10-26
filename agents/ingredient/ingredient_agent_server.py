"""
uAgents REST server for ingredient agent with webhook endpoints
"""

import sys
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from uagents import Agent, Context, Protocol
    from uagents_core.contrib.protocols.chat import (
        ChatAcknowledgement,
        ChatMessage,
        TextContent,
        AgentContent,
        StartSessionContent,
        EndSessionContent,
        chat_protocol_spec
    )
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(f"Missing required dependencies: {e}. Please install uagents.")

from ingredient.src.ingredient_agent import IngredientAgent


# Initialize the ingredient agent
ingredient_agent = IngredientAgent()

# Global variable to store the latest report
latest_report = None

# Load restaurants configuration
restaurants = []
try:
    restaurants_file = os.path.join(os.path.dirname(__file__), '..', 'restaurants.json')
    if os.path.exists(restaurants_file):
        with open(restaurants_file, 'r') as f:
            config = json.load(f)
            restaurants = config.get('restaurants', [])
except Exception as e:
    print(f"Error loading restaurants config: {e}")


def get_restaurant_by_secure_key(secure_key: str) -> Optional[Dict[str, Any]]:
    """Get restaurant info by secure_key"""
    for restaurant in restaurants:
        if restaurant.get('secure_key') == secure_key:
            return restaurant
    return None


def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Get restaurant info by restaurant_id"""
    for restaurant in restaurants:
        if restaurant.get('id') == restaurant_id:
            return restaurant
    return None


def get_available_restaurants() -> List[Dict[str, str]]:
    """Get list of available restaurants for error messages"""
    return [{"id": r["id"], "name": r["name"]} for r in restaurants]

# Create uAgents agent
agent = Agent(
    name="ingredient_agent_v2",
    seed="ingredient-agent-seed-12345-v2",
    port=8004,
    mailbox=True
)

# Initialize chat protocol
protocol = Protocol(spec=chat_protocol_spec)


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
        with open('data/inventory_report.json', 'r') as f:
            latest_report = json.load(f)
        print(f"Loaded inventory report from file")
    except FileNotFoundError:
        print("No existing inventory report found, will generate on first request")
        latest_report = None
    except Exception as e:
        print(f"Error loading inventory report: {e}")
        latest_report = None


def truncate_ingredient_context(report: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate ingredient data to protect sensitive information"""
    truncated = {
        "metadata": {
            "generated_at": report.get("metadata", {}).get("generated_at"),
            "restaurant_key": report.get("metadata", {}).get("restaurant_key")
        }
    }
    
    # Include only ingredient names for allergy identification
    if "current_stock" in report:
        ingredient_names = []
        for item in report["current_stock"]:
            if item.get("available", True):  # Only include available ingredients
                ingredient_names.append({
                    "name": item.get("name", ""),
                    "unit": item.get("unit", "")
                })
        truncated["ingredients"] = ingredient_names
        truncated["total_ingredients"] = len(ingredient_names)
    
    # Include top 5 most used ingredients (if available)
    if "consumption_analysis" in report and "top_ingredients" in report["consumption_analysis"]:
        top_ingredients = report["consumption_analysis"]["top_ingredients"][:5]
        truncated["top_ingredients"] = [
            {"name": item.get("name", ""), "usage_frequency": item.get("usage_frequency", 0)}
            for item in top_ingredients
        ]
    
    # Include low stock alerts (names only, no quantities or costs)
    if "low_stock_alerts" in report:
        truncated["low_stock_alerts"] = [
            {"name": alert.get("name", ""), "unit": alert.get("unit", "")}
            for alert in report["low_stock_alerts"]
        ]
    
    return truncated


@agent.on_interval(period=86400)  # 24 hours in seconds
async def update_inventory_report(ctx: Context):
    """Update inventory report daily for all restaurants"""
    global latest_report
    try:
        print("Updating multi-restaurant inventory report...")
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'inventory_report.json')
        latest_report = ingredient_agent.generate_multi_restaurant_report(data_path)
        print("Multi-restaurant inventory report updated")  
    except Exception as e:
        ctx.logger.error(f"Error updating inventory report: {e}")


@agent.on_rest_get("/inventory_report", InventoryReportResponse)
async def handle_inventory_report(ctx: Context, secure_key: str = None) -> InventoryReportResponse:
    """Handle GET requests for comprehensive inventory report"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Wrap in restaurant context for consistency
        restaurant_report = {
            "restaurant_id": restaurant["id"],
            "restaurant_name": restaurant["name"],
            "analytics": report
        }
        
        return InventoryReportResponse(response=json.dumps(restaurant_report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting inventory report: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/low_stock", LowStockResponse)
async def handle_low_stock_alerts(ctx: Context, secure_key: str = None) -> LowStockResponse:
    """Handle GET requests for low stock alerts"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return LowStockResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return LowStockResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return ReorderSuggestionsResponse(response=json.dumps(resp))
        
        # Extract low stock alerts from the report
        if report and 'low_stock_alerts' in report:
            alerts = report['low_stock_alerts']
        else:
            alerts = []
        
        return LowStockResponse(response=json.dumps(alerts, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting low stock alerts: {e}")
        return LowStockResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/reorder_suggestions", ReorderSuggestionsResponse)
async def handle_reorder_suggestions(ctx: Context, secure_key: str = None) -> ReorderSuggestionsResponse:
    """Handle GET requests for reorder suggestions"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return ReorderSuggestionsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return ReorderSuggestionsResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Extract reorder suggestions from the report
        if report and 'reorder_suggestions' in report:
            suggestions = report['reorder_suggestions']
        else:
            suggestions = []
        
        return ReorderSuggestionsResponse(response=json.dumps(suggestions, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting reorder suggestions: {e}")
        return ReorderSuggestionsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/consumption_analysis", InventoryReportResponse)
async def handle_consumption_analysis(ctx: Context, secure_key: str = None) -> InventoryReportResponse:
    """Handle GET requests for consumption pattern analysis"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Extract consumption analysis from the report
        if report and 'consumption_analysis' in report:
            analysis = report['consumption_analysis']
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
async def handle_usage_summary(ctx: Context, secure_key: str = None) -> InventoryReportResponse:
    """Handle GET requests for ingredient usage summary"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Extract usage summary from the report
        if report and 'usage_summary' in report:
            summary = report['usage_summary']
        else:
            summary = {"message": "No usage summary available"}
        
        return InventoryReportResponse(response=json.dumps(summary, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting usage summary: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/metrics", InventoryReportResponse)
async def handle_metrics(ctx: Context, secure_key: str = None) -> InventoryReportResponse:
    """Handle GET requests for dashboard metrics"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = ingredient_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return InventoryReportResponse(response=json.dumps(resp))
        
        if not report:
            return InventoryReportResponse(response=json.dumps({
                "lowStock": [],
                "unavailable": [],
                "totalItems": 0,
                "timestamp": datetime.now().isoformat()
            }))

        stock = report.get('current_stock', [])

        # Identify low stock items (quantity < 1.0)
        low_stock = [
            {"name": item['name'], "quantity": item['quantity'], "unit": item['unit']}
            for item in stock
            if item.get('available', True) and item.get('quantity', 0) < 1.0
        ]

        # Identify unavailable items
        unavailable = [
            {"name": item['name'], "quantity": item['quantity'], "unit": item['unit']}
            for item in stock
            if not item.get('available', True)
        ]

        metrics = {
            "lowStock": low_stock,
            "unavailable": unavailable,
            "totalItems": len(stock),
            "activeItems": len([i for i in stock if i.get('available', True)]),
            "timestamp": report.get('metadata', {}).get('generated_at', datetime.now().isoformat())
        }

        return InventoryReportResponse(response=json.dumps(metrics))
    except Exception as e:
        ctx.logger.error(f"Error getting metrics: {e}")
        return InventoryReportResponse(response=json.dumps({"error": str(e)}))


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and respond with ingredient analytics"""
    try:
        # Step 1: Send acknowledgement
        await ctx.send(
            sender,
            ChatAcknowledgement(
                timestamp=datetime.now(),
                acknowledged_msg_id=msg.msg_id
            ),
        )
        
        # Step 2: Check if user message
        ctx.logger.info(f"Received message from {sender}: {msg}")
        
        ctx.logger.info("Processing user message...")
        
        # Step 3: Extract restaurant_id and user question from message content
        restaurant_id = None
        user_question = None
        full_message_text = ""
        
        if hasattr(msg, 'content') and msg.content:
            for content in msg.content:
                if hasattr(content, 'text'):
                    full_message_text = content.text.strip()
                    user_question = full_message_text
        
        # If no question provided, set a default question
        if not user_question:
            user_question = "Please provide a summary of this restaurant's ingredient inventory and any important alerts."
        
        # If no explicit restaurant_id found, use Claude to try to identify it from the message
        if not restaurant_id and full_message_text:
            try:
                # Import ClaudeWrapper here to avoid circular imports
                from ingredient.src.analytics.llm_analyzer import LLMAnalyzer
                claude_wrapper = LLMAnalyzer()
                
                # Load available restaurant IDs from restaurants.json
                available_restaurant_ids = [r["id"] for r in restaurants]
                restaurant_names = {r["id"]: r["name"] for r in restaurants}
                
                # Create prompt for Claude to identify restaurant
                restaurant_identification_prompt = f"""Given the following user message, identify if it mentions a restaurant from the available list. Return ONLY the restaurant_id if found, or "NOT_FOUND" if not found.

Available restaurants:
{json.dumps(restaurant_names, indent=2)}

User message: {full_message_text}

Return format (one of):
- "restaurant_id: <exact_restaurant_id>" if you can confidently identify the restaurant
- "NOT_FOUND" if you cannot confidently identify any restaurant

Examples:
- "What ingredients does Cote Ouest have?" → "restaurant_id: cote-ouest-bistro-sf"
- "Tell me about Causwells inventory" → "restaurant_id: causwells-sf"
- "What's the weather like?" → "NOT_FOUND"
- "Show me ingredients for the French bistro" → "restaurant_id: cote-ouest-bistro-sf"
"""

                # Ask Claude to identify the restaurant
                identification_response = claude_wrapper.client.messages.create(
                    model=claude_wrapper.model,
                    max_tokens=200,
                    temperature=0.1,  # Low temperature for deterministic extraction
                    messages=[{
                        "role": "user",
                        "content": restaurant_identification_prompt
                    }]
                )
                
                identification_result = identification_response.content[0].text.strip()
                
                # Parse the result
                if identification_result.startswith("restaurant_id:"):
                    restaurant_id = identification_result.split("restaurant_id:")[1].strip()
                    ctx.logger.info(f"Claude identified restaurant_id: {restaurant_id}")
                else:
                    response = "Error: No restaurant could be identified from your message. Please specify a restaurant name or ID. Available restaurants: " + json.dumps(restaurant_names, indent=2)
                    ctx.logger.warning("Could not identify restaurant from message")
                    restaurant_id = None
                
            except Exception as e:
                response = f"Error identifying restaurant: {str(e)}"
                ctx.logger.error(f"Error identifying restaurant: {e}")
                restaurant_id = None
        
        if not restaurant_id:
            if 'response' not in locals():
                restaurant_names = {r["id"]: r["name"] for r in restaurants}
                response = "Error: restaurant_id is required. Please provide a restaurant ID in your message. Available restaurants: " + json.dumps(restaurant_names, indent=2)
            ctx.logger.warning("No restaurant_id available")
        else:
            # Step 4: Generate analytics for specific restaurant and answer with Claude
            try:
                # Find restaurant by ID to get secure_key
                restaurant = get_restaurant_by_id(restaurant_id)
                if not restaurant:
                    response = f"Error: Restaurant {restaurant_id} not found."
                    ctx.logger.error(f"Restaurant {restaurant_id} not found")
                else:
                    secure_key = restaurant["secure_key"]
                    
                    # Load analytics report for the restaurant
                    report = ingredient_agent.load_report(secure_key)
                    if not report:
                        response = f"Error: No ingredient report found for restaurant {restaurant_id}."
                        ctx.logger.error(f"No report found for restaurant {restaurant_id}")
                    else:
                        # Apply truncation to protect sensitive data
                        # print("report: ", json.dumps(report, indent=2))
                        truncated_report = truncate_ingredient_context(report)
                        ctx.logger.info(f"Loaded and truncated ingredient report for restaurant: {restaurant_id}")

                        # Use Claude API to answer user's question with truncated analytics context
                        from ingredient.src.analytics.llm_analyzer import LLMAnalyzer
                        claude_wrapper = LLMAnalyzer()
                        
                        # Create prompt with truncated analytics context
                        prompt = f"""You are a restaurant ingredient inventory assistant. Analyze the following ingredient data and answer the user's question.

Restaurant: {restaurant["name"]} ({restaurant_id})

Ingredient Data (JSON):
{json.dumps(truncated_report, indent=2)}

User Question: {user_question}

Please provide a clear, helpful answer based on the ingredient data above. Focus on:
- Available ingredients (for allergy identification)
- Low stock alerts
- Top ingredients by usage
- General inventory status

Be specific and reference specific ingredients when relevant."""

                        # Get response from Claude
                        claude_response = claude_wrapper.client.messages.create(
                            model=claude_wrapper.model,
                            max_tokens=4000,
                            temperature=0.7,
                            messages=[{
                                "role": "user",
                                "content": prompt
                            }]
                        )
                        
                        response = claude_response.content[0].text
                        ctx.logger.info(f"Claude API response generated successfully for restaurant: {restaurant_id}")
                
            except Exception as e:
                response = f"Error processing request for restaurant {restaurant_id}: {str(e)}"
                ctx.logger.error(f"Error processing request for restaurant {restaurant_id}: {e}")
        
        # Step 5: Send response
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.now(),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=response),
                EndSessionContent(type="end-session")
            ]
        ))
        
        ctx.logger.info("Response sent successfully")
        
    except Exception as e:
        ctx.logger.error(f"Error handling message: {e}")
        # Send error response
        try:
            await ctx.send(sender, ChatMessage(
                timestamp=datetime.now(),
                msg_id=uuid4(),
                content=[
                    TextContent(type="text", text=f"Error processing request: {str(e)}"),
                    EndSessionContent(type="end-session")
                ]
            ))
        except Exception as send_error:
            ctx.logger.error(f"Error sending error response: {send_error}")


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements"""
    ctx.logger.info(f"Received acknowledgement from {sender}")


# Register the protocol with the agent
agent.include(protocol, publish_manifest=True)


if __name__ == "__main__":
    print("Starting Ingredient Agent REST Server...")
    print("Available endpoints:")
    print("  GET /metrics?secure_key=<uuid> - Dashboard metrics (low stock, unavailable items)")
    print("  GET /inventory_report?secure_key=<uuid> - Full inventory report")
    print("  GET /low_stock?secure_key=<uuid> - Low stock alerts")
    print("  GET /reorder_suggestions?secure_key=<uuid> - Reorder suggestions")
    print("  GET /consumption_analysis?secure_key=<uuid> - Consumption analysis")
    print("  GET /usage_summary?secure_key=<uuid> - Usage summary")
    print(f"Server running on http://localhost:8004")
    print("Multi-restaurant report will be updated daily at midnight")
    
    # Load existing report on startup
    load_inventory_report()
    
    agent.run()
