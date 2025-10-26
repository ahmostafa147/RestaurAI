"""
uAgents REST server for staff agent with webhook endpoints
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

from staff.src.staff_agent import StaffAgent


# Initialize the staff agent
staff_agent = StaffAgent()

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
    name="staff_agent_v1",
    seed="staff-agent-seed-12345-v1",
    port=8010,
    mailbox=True
)

# Initialize chat protocol
protocol = Protocol(spec=chat_protocol_spec)


# Pydantic models for REST endpoints
class ScheduleReportResponse(BaseModel):
    response: str

class WeaknessesResponse(BaseModel):
    response: str

class AbsenceHandlingResponse(BaseModel):
    response: str

class CoverageMetricsResponse(BaseModel):
    response: str

class ErrorResponse(BaseModel):
    error: str


def load_schedule_report():
    """Load the latest schedule report from JSON file"""
    global latest_report
    try:
        # Load from data directory similar to analytics_report.json
        report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schedule_report.json')
        with open(report_path, 'r') as f:
            latest_report = json.load(f)
        print(f"Loaded schedule report from {report_path}")
    except FileNotFoundError:
        print("No existing schedule report found, will generate on first request")
        latest_report = None
    except Exception as e:
        print(f"Error loading schedule report: {e}")
        latest_report = None


def truncate_staff_context(report: Dict[str, Any]) -> Dict[str, Any]:
    """Truncate staff data to protect sensitive information"""
    truncated = {
        "metadata": {
            "generated_at": report.get("metadata", {}).get("generated_at"),
            "restaurant_key": report.get("metadata", {}).get("restaurant_key")
        }
    }
    
    # Include coverage summary
    if "summary" in report:
        truncated["summary"] = report["summary"]
    
    # Include weakness counts (no sensitive details)
    if "weaknesses" in report:
        weaknesses = report["weaknesses"]
        truncated["weakness_summary"] = {
            "understaffed_slots": len(weaknesses.get("understaffed_slots", [])),
            "overstaffed_slots": len(weaknesses.get("overstaffed_slots", [])),
            "overworked_staff": len(weaknesses.get("overworked_staff", [])),
            "underutilized_staff": len(weaknesses.get("underutilized_staff", []))
        }
    
    # Include LLM insights (safe for sharing)
    if "llm_insights" in report:
        truncated["llm_insights"] = report["llm_insights"]
    
    return truncated


@agent.on_interval(period=86400)  # 24 hours in seconds
async def update_schedule_report(ctx: Context):
    """Update schedule report daily for all restaurants"""
    global latest_report
    try:
        print("Updating multi-restaurant schedule report...")
        # Save to data directory similar to analytics_report.json
        output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schedule_report.json')
        latest_report = staff_agent.generate_multi_restaurant_report(output_path)
        print(f"Multi-restaurant schedule report updated and saved to {output_path}")
    except Exception as e:
        ctx.logger.error(f"Error updating schedule report: {e}")


@agent.on_rest_get("/schedule_report", ScheduleReportResponse)
async def handle_schedule_report(ctx: Context, secure_key: str = None) -> ScheduleReportResponse:
    """Handle GET requests for comprehensive schedule report"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Generate report for specific restaurant
        report = staff_agent.load_report(secure_key)
        if not report:
            resp = {
                "error": "No report found for this restaurant"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Wrap in restaurant context for consistency
        restaurant_report = {
            "restaurant_id": restaurant["id"],
            "restaurant_name": restaurant["name"],
            "analytics": report
        }
        
        return ScheduleReportResponse(response=json.dumps(restaurant_report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting schedule report: {e}")
        return ScheduleReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/weaknesses", WeaknessesResponse)
async def handle_weaknesses(ctx: Context, secure_key: str = None) -> WeaknessesResponse:
    """Handle GET requests for schedule weaknesses"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return WeaknessesResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return WeaknessesResponse(response=json.dumps(resp))
        
        # Generate weakness report for specific restaurant
        report = staff_agent.identify_weaknesses(secure_key)
        if not report:
            resp = {
                "error": "No weakness report found for this restaurant"
            }
            return WeaknessesResponse(response=json.dumps(resp))
        
        return WeaknessesResponse(response=json.dumps(report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting weaknesses: {e}")
        return WeaknessesResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/handle_absence", AbsenceHandlingResponse)
async def handle_absence(ctx: Context, secure_key: str = None, staff_id: int = None, date: str = None) -> AbsenceHandlingResponse:
    """Handle GET requests for absence handling"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return AbsenceHandlingResponse(response=json.dumps(resp))
        
        if not staff_id:
            resp = {
                "error": "staff_id parameter is required"
            }
            return AbsenceHandlingResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return AbsenceHandlingResponse(response=json.dumps(resp))
        
        # Generate absence handling report
        report = staff_agent.handle_absence(secure_key, staff_id, date)
        if not report:
            resp = {
                "error": "No absence handling report found for this restaurant"
            }
            return AbsenceHandlingResponse(response=json.dumps(resp))
        
        return AbsenceHandlingResponse(response=json.dumps(report, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error handling absence: {e}")
        return AbsenceHandlingResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/coverage_metrics", CoverageMetricsResponse)
async def handle_coverage_metrics(ctx: Context, secure_key: str = None) -> CoverageMetricsResponse:
    """Handle GET requests for coverage metrics"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return CoverageMetricsResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return CoverageMetricsResponse(response=json.dumps(resp))
        
        # Generate coverage metrics for specific restaurant
        metrics = staff_agent.get_coverage_metrics(secure_key)
        if not metrics:
            resp = {
                "error": "No coverage metrics found for this restaurant"
            }
            return CoverageMetricsResponse(response=json.dumps(resp))
        
        return CoverageMetricsResponse(response=json.dumps(metrics, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting coverage metrics: {e}")
        return CoverageMetricsResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/utilization", ScheduleReportResponse)
async def handle_utilization(ctx: Context, secure_key: str = None) -> ScheduleReportResponse:
    """Handle GET requests for staff utilization analysis"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Generate utilization analysis for specific restaurant
        utilization = staff_agent.analyze_staff_utilization(secure_key)
        if not utilization:
            resp = {
                "error": "No utilization analysis found for this restaurant"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        return ScheduleReportResponse(response=json.dumps(utilization, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting utilization: {e}")
        return ScheduleReportResponse(response=json.dumps({"error": str(e)}))


@agent.on_rest_get("/optimization", ScheduleReportResponse)
async def handle_optimization(ctx: Context, secure_key: str = None) -> ScheduleReportResponse:
    """Handle GET requests for schedule optimization recommendations"""
    try:
        if not secure_key:
            resp = {
                "error": "secure_key parameter is required"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Validate secure_key
        restaurant = get_restaurant_by_secure_key(secure_key)
        if not restaurant:
            resp = {
                "error": "Invalid secure_key"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        # Generate optimization recommendations for specific restaurant
        optimization = staff_agent.optimize_schedule(secure_key)
        if not optimization:
            resp = {
                "error": "No optimization recommendations found for this restaurant"
            }
            return ScheduleReportResponse(response=json.dumps(resp))
        
        return ScheduleReportResponse(response=json.dumps({"recommendations": optimization}, indent=2))
    except Exception as e:
        ctx.logger.error(f"Error getting optimization: {e}")
        return ScheduleReportResponse(response=json.dumps({"error": str(e)}))


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and respond with staff analytics"""
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
            user_question = "Please provide a summary of this restaurant's staff schedule and any important alerts."
        
        # If no explicit restaurant_id found, use Claude to try to identify it from the message
        if not restaurant_id and full_message_text:
            try:
                # Import LLMAnalyzer here to avoid circular imports
                from staff.src.analytics.llm_analyzer import LLMAnalyzer
                llm_analyzer = LLMAnalyzer()
                
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
- "What staff does Cote Ouest have?" → "restaurant_id: cote-ouest-bistro-sf"
- "Tell me about Causwells schedule" → "restaurant_id: causwells-sf"
- "What's the weather like?" → "NOT_FOUND"
- "Show me staff for the French bistro" → "restaurant_id: cote-ouest-bistro-sf"
"""

                # Ask Claude to identify the restaurant
                identification_response = llm_analyzer.client.messages.create(
                    model=llm_analyzer.model,
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
                    report = staff_agent.load_report(secure_key)
                    if not report:
                        response = f"Error: No staff report found for restaurant {restaurant_id}."
                        ctx.logger.error(f"No report found for restaurant {restaurant_id}")
                    else:
                        # Apply truncation to protect sensitive data
                        truncated_report = truncate_staff_context(report)
                        ctx.logger.info(f"Loaded and truncated staff report for restaurant: {restaurant_id}")

                        # Use Claude API to answer user's question with truncated analytics context
                        from staff.src.analytics.llm_analyzer import LLMAnalyzer
                        llm_analyzer = LLMAnalyzer()
                        
                        # Create prompt with truncated analytics context
                        prompt = f"""You are a restaurant staff scheduling assistant. Analyze the following staff data and answer the user's question.

Restaurant: {restaurant["name"]} ({restaurant_id})

Staff Data (JSON):
{json.dumps(truncated_report, indent=2)}

User Question: {user_question}

Please provide a clear, helpful answer based on the staff data above. Focus on:
- Schedule coverage and weaknesses
- Staff utilization patterns
- Absence handling recommendations
- Optimization opportunities

Be specific and reference specific issues when relevant."""

                        # Get response from Claude
                        claude_response = llm_analyzer.client.messages.create(
                            model=llm_analyzer.model,
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
    print("Starting Staff Agent REST Server...")
    print("Available endpoints:")
    print("  GET /schedule_report?secure_key=<uuid> - Full schedule analysis")
    print("  GET /weaknesses?secure_key=<uuid> - Identify schedule issues")
    print("  GET /handle_absence?secure_key=<uuid>&staff_id=<id>&date=<date> - Absence handling")
    print("  GET /coverage_metrics?secure_key=<uuid> - Coverage statistics")
    print("  GET /utilization?secure_key=<uuid> - Staff utilization analysis")
    print("  GET /optimization?secure_key=<uuid> - Schedule optimization recommendations")
    print(f"Server running on http://localhost:8010")
    print("Multi-restaurant report will be updated daily at midnight")
    
    # Load existing report on startup
    load_schedule_report()
    
    agent.run()
