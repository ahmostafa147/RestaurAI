"""
uAgents REST server for menu agent with webhook endpoints
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

from menu.src.menu_agent import MenuAgent


# Initialize the menu agent
menu_agent = MenuAgent()

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
    name="menu_agent_v2",
    seed="menu-agent-seed-12345-v2",
    port=8006,
    mailbox=True

)

# Initialize chat protocol
protocol = Protocol(spec=chat_protocol_spec)


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


def truncate_menu_context(report: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate menu data to protect sensitive business information"""
    truncated = {
        "metadata": {
            "generated_at": report.get("metadata", {}).get("generated_at"),
            "restaurant_key": report.get("metadata", {}).get("restaurant_key")
        }
    }
    
    # Include menu items with consumer-facing information
    if "menu_items" in report:
        menu_items = []
        for item in report["menu_items"]:
            # Include consumer-facing information only
            truncated_item = {
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "category": item.get("category", ""),
                "price": item.get("price", 0.0),  # Consumer price
                "available": item.get("available", True)
            }
            
            # Include ingredient names only (for allergies), no costs
            if "ingredients" in item:
                truncated_item["ingredients"] = [
                    {
                        "name": ing.get("name", ""),
                        "unit": ing.get("unit", "")
                    }
                    for ing in item["ingredients"]
                ]
            
            menu_items.append(truncated_item)
        
        truncated["menu_items"] = menu_items
        truncated["total_items"] = len(menu_items)
    
    # Include basic analytics without sensitive details
    if "summary_metrics" in report:
        summary = report["summary_metrics"]
        truncated["summary"] = {
            "total_menu_items": summary.get("total_menu_items", 0),
            "available_items": summary.get("available_items", 0),
            "categories": summary.get("categories", [])
        }
    
    # Include popular items (names only, no revenue details)
    if "item_analytics" in report and "popular_items" in report["item_analytics"]:
        popular_items = report["item_analytics"]["popular_items"][:5]  # Top 5
        truncated["popular_items"] = [
            {
                "name": item.get("name", ""),
                "category": item.get("category", ""),
                "order_count": item.get("order_count", 0)
            }
            for item in popular_items
        ]
    
    # Include recommendations (general advice, no specific financial details)
    if "llm_insights" in report and "recommendations" in report["llm_insights"]:
        truncated["recommendations"] = report["llm_insights"]["recommendations"]
    
    return truncated


@agent.on_interval(period=86400)  # 24 hours in seconds
async def update_menu_report(ctx: Context):
    """Update menu report daily for all restaurants"""
    global latest_report
    try:
        print("Updating multi-restaurant menu analytics report...")
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'multi_restaurant_report.json')
        latest_report = menu_agent.generate_multi_restaurant_report(data_path)
        print("Multi-restaurant menu analytics report updated")
    except Exception as e:
        ctx.logger.error(f"Error updating menu report: {e}")


@agent.on_rest_get("/menu_analytics", MenuReportResponse)
async def handle_menu_analytics(ctx: Context, secure_key: str = None) -> MenuReportResponse:
    """Handle GET requests for comprehensive menu analytics report"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return MenuReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = menu_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return MenuReportResponse(response=json.dumps(resp))
        # Wrap in restaurant context for consistency
        restaurant_report = {
            "restaurant_id": restaurant["id"],
            "restaurant_name": restaurant["name"],
            "analytics": report
        }
        
        return MenuReportResponse(response=json.dumps(restaurant_report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu analytics: {e}")
        return MenuReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/menu_performance", MenuPerformanceResponse)
async def handle_menu_performance(ctx: Context, secure_key: str = None) -> MenuPerformanceResponse:
    """Handle GET requests for menu performance metrics"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return MenuPerformanceResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuPerformanceResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one

        report = menu_agent.generate_analytics_report(secure_key)
        
        # Extract performance metrics from the report
        if report and 'summary_metrics' in report:
            performance = report['summary_metrics']
        else:
            performance = {"message": "No performance metrics available"}
        
        return MenuPerformanceResponse(response=json.dumps(performance, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu performance: {e}")
        return MenuPerformanceResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/popular_items", MenuAnalyticsResponse)
async def handle_popular_items(ctx: Context, secure_key: str = None) -> MenuAnalyticsResponse:
    """Handle GET requests for popular menu items analysis"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = menu_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Extract popular items from the report
        if report and 'item_analytics' in report:
            popular_items = report['item_analytics'].get('popular_items', [])
        else:
            popular_items = {"message": "No popular items data available"}
        
        return MenuAnalyticsResponse(response=json.dumps(popular_items, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting popular items: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/profit_analysis", MenuAnalyticsResponse)
async def handle_profit_analysis(ctx: Context, secure_key: str = None) -> MenuAnalyticsResponse:
    """Handle GET requests for profit analysis"""
    try:
        if not secure_key:
            available_restaurants = get_available_restaurants()
            resp = {
                "error": "secure_key parameter is required",
                "available_restaurants": available_restaurants
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = menu_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Extract profit analysis from the report
        if report and 'item_analytics' in report:
            profit_analysis = report['item_analytics'].get('profit_analysis', {})
        else:
            profit_analysis = {"message": "No profit analysis available"}
        
        return MenuAnalyticsResponse(response=json.dumps(profit_analysis, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting profit analysis: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/menu_recommendations", MenuAnalyticsResponse)
async def handle_menu_recommendations(ctx: Context, secure_key: str = None) -> MenuAnalyticsResponse:
    """Handle GET requests for menu recommendations"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = menu_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Extract recommendations from the report
        if report and 'llm_insights' in report:
            recommendations = report['llm_insights'].get('recommendations', [])
        else:
            recommendations = {"message": "No recommendations available"}
        
        return MenuAnalyticsResponse(response=json.dumps(recommendations, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting menu recommendations: {e}")
        return MenuAnalyticsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/revenue_analysis", MenuAnalyticsResponse)
async def handle_revenue_analysis(ctx: Context, secure_key: str = None) -> MenuAnalyticsResponse:
    """Handle GET requests for revenue analysis"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        #try to load already generated report, instead of generating new one
        report = menu_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return MenuAnalyticsResponse(response=json.dumps(resp))
        
        # Extract revenue analysis from the report
        if report and 'revenue_analytics' in report:
            revenue_analysis = report['revenue_analytics']
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


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and respond with menu analytics"""
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
            user_question = "Please provide a summary of this restaurant's menu and popular items."
        
        # If no explicit restaurant_id found, use Claude to try to identify it from the message
        if not restaurant_id and full_message_text:
            try:
                # Import LLMAnalyzer here to avoid circular imports
                from menu.src.analytics.llm_analyzer import LLMAnalyzer
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
- "What's on the menu at Cote Ouest?" → "restaurant_id: cote-ouest-bistro-sf"
- "Tell me about Causwells menu" → "restaurant_id: causwells-sf"
- "What's the weather like?" → "NOT_FOUND"
- "Show me the French bistro menu" → "restaurant_id: cote-ouest-bistro-sf"
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
                    response = "Error: No restaurant could be identified from your message. Please specify a restaurant name or ID."
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
                    report = menu_agent.load_report(secure_key)
                    if not report:
                        response = f"Error: No menu report found for restaurant {restaurant_id}."
                        ctx.logger.error(f"No report found for restaurant {restaurant_id}")
                    else:
                        # Apply truncation to protect sensitive data
                        # print("report: ", json.dumps(report, indent=2))
                        truncated_report = truncate_menu_context(report)
                        ctx.logger.info(f"Loaded and truncated menu report for restaurant: {restaurant_id}")

                        # Use Claude API to answer user's question with truncated analytics context
                        from menu.src.analytics.llm_analyzer import LLMAnalyzer
                        claude_wrapper = LLMAnalyzer()
                        
                        # Create prompt with truncated analytics context
                        prompt = f"""You are a restaurant menu assistant. Analyze the following menu data and answer the user's question.

Restaurant: {restaurant["name"]} ({restaurant_id})

Menu Data (JSON):
{json.dumps(truncated_report, indent=2)}

User Question: {user_question}

Please provide a clear, helpful answer based on the menu data above. Focus on:
- Available menu items and their descriptions
- Ingredient lists (for allergy identification)
- Popular items
- Menu categories and organization
- Consumer prices

Be specific and reference specific menu items when relevant."""

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
    print("Starting Menu Agent REST Server...")
    print("Available endpoints:")
    print("  GET /menu_analytics?secure_key=<uuid> - Full menu analytics report")
    print("  GET /menu_performance?secure_key=<uuid> - Menu performance metrics")
    print("  GET /popular_items?secure_key=<uuid> - Popular menu items analysis")
    print("  GET /profit_analysis?secure_key=<uuid> - Profit analysis")
    print("  GET /menu_recommendations?secure_key=<uuid> - Menu recommendations")
    print("  GET /revenue_analysis?secure_key=<uuid> - Revenue analysis")
    print("  GET /available_reports - List of available reports")
    print(f"Server running on http://localhost:8006")
    print("Multi-restaurant report will be updated daily at midnight")
    
    # Load existing report on startup
    load_menu_report()
    
    agent.run()
