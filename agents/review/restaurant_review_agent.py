"""
Restaurant Review Agent for AgentVerse
uAgent that responds to chat messages with analytics reports and refreshes reviews daily.
"""

import sys
import os
import asyncio
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

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

from main import RestaurantReviewAgent
from scrapers.pull_dataset import Status
from analytics.analytics_engine import AnalyticsEngine
from eval.llm_wrapper import ClaudeWrapper


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for REST endpoint
class ChatRequest(BaseModel):
    message: str
    restaurant_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

# Configuration
REFRESH_INTERVAL_SECONDS = 86400  # 24 hours as constant variable
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'database.json')

# Initialize the restaurant review agent
restaurant_agent = RestaurantReviewAgent(DATABASE_PATH)

# Initialize the uAgent
agent = Agent(
    name="restaurant-review-agent-v2",
    seed="restaurant_review_agent_seed_2025_v2",
    port=8003,
    mailbox=True
)

# Initialize chat protocol
protocol = Protocol(spec=chat_protocol_spec)

# REST endpoint for analytics report
@agent.on_rest_get("/analytics", ChatResponse)
async def handle_fast_chat(ctx: Context, restaurant_id: str = None) -> ChatResponse:
    """Handle GET requests for analytics report"""
    try:
        if not restaurant_id:
            restaurant_ids = []
            try:
                restaurants_file = os.path.join(os.path.dirname(__file__), '..', 'restaurants.json')
                if os.path.exists(restaurants_file):
                    with open(restaurants_file, 'r') as f:
                        config = json.load(f)
                        restaurant_ids = [r["id"] for r in config.get('restaurants', [])]
            except Exception as e:
                ctx.logger.error(f"Error loading restaurants: {e}")
            resp = {
                "error": "restaurant_id parameter is required",
                "available_restaurant_ids": restaurant_ids
            }
            return ChatResponse(response=json.dumps(resp))
        
        # Generate analytics for specific restaurant
        engine = AnalyticsEngine(restaurant_agent.database_handler)
        report = engine.generate_full_report(restaurant_id=restaurant_id)
        
        return ChatResponse(response=json.dumps(report, indent=2))
    except FileNotFoundError:
        return ChatResponse(response=json.dumps({"error": "Analytics report not found. Please wait for the daily refresh to complete."}))
    except Exception as e:
        ctx.logger.error(f"Error generating analytics: {e}")
        return ChatResponse(response=json.dumps({"error": str(e)}))

@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and respond with analytics report"""
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
        
        # If no question provided but restaurant_id exists, set a default question
        if not user_question:
            user_question = "Please provide a summary of this restaurant's analytics based on the reviews."
        
        # If no explicit restaurant_id found, use Claude to try to identify it from the message
        if not restaurant_id and full_message_text:
            try:
                claude_wrapper = ClaudeWrapper()
                
                # Load available restaurant IDs from restaurants.json
                restaurants_file = os.path.join(os.path.dirname(__file__), '..', 'restaurants.json')
                with open(restaurants_file, 'r') as f:
                    config = json.load(f)
                    restaurants = config.get('restaurants', [])
                
                restaurant_names = {r["id"]: r["name"] for r in restaurants}
                available_restaurant_ids = [r["id"] for r in restaurants]
                
                # Create prompt for Claude to identify restaurant
                restaurant_identification_prompt = f"""Given the following user message, identify if it mentions a restaurant from the available list. Return ONLY the restaurant_id if found, or "NOT_FOUND" if not found.

Available restaurants:
{json.dumps(restaurant_names, indent=2)}

User message: {full_message_text}

Return format (one of):
- "restaurant_id: <exact_restaurant_id>" if you can identify the restaurant
- "NOT_FOUND" if you cannot identify an applicable restaurant

Examples:
- "What do customers think about Cote Ouest?" → "restaurant_id: cote-ouest-bistro-sf"
- "Tell me about Causwells reviews" → "restaurant_id: causwells-sf"
- "What's the weather like?" → "NOT_FOUND"
- "Show me analytics for the French bistro" → "restaurant_id: cote-ouest-bistro-sf"
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
                    # Set default question if no explicit question was found
                    if not user_question:
                        user_question = full_message_text
                else:
                    response = "Error: No restaurant could be identified from your message. Please specify a restaurant name or ID."
                    ctx.logger.warning("Could not identify restaurant from message")
                    restaurant_id = None  # Ensure it's None so we skip the analytics section
                
            except Exception as e:
                response = f"Error identifying restaurant: {str(e)}"
                ctx.logger.error(f"Error identifying restaurant: {e}")
                restaurant_id = None
        
        if not restaurant_id:
            if 'response' not in locals():
                # Load restaurant names for error message
                try:
                    restaurants_file = os.path.join(os.path.dirname(__file__), '..', 'restaurants.json')
                    with open(restaurants_file, 'r') as f:
                        config = json.load(f)
                        restaurants = config.get('restaurants', [])
                    restaurant_names = {r["id"]: r["name"] for r in restaurants}
                    response = "Error: restaurant_id is required. Please provide a restaurant ID in your message. Available restaurants: " + json.dumps(restaurant_names, indent=2)
                except Exception as e:
                    response = "Error: restaurant_id is required. Please provide a restaurant ID in your message."
            ctx.logger.warning("No restaurant_id available")
        else:
            # Step 4: Generate analytics for specific restaurant and answer with Claude
            try:
                # Generate restaurant-specific analytics
                # Use pre-generated analytics report from analytics_report.json

                analytics_path = os.path.join(os.path.dirname(__file__),'..', '..', 'data', 'analytics_report.json')
                try:
                    with open(analytics_path, "r", encoding="utf-8") as f:
                        analytics_data = json.load(f)
                except FileNotFoundError:
                    ctx.logger.error("analytics_report.json not found.")
                    raise

                restaurants = analytics_data.get("restaurants", {})
                restaurant_analytics = restaurants.get(restaurant_id, {})
                if not restaurant_analytics:
                    raise ValueError(f"No analytics data found for restaurant_id: {restaurant_id}")

                report = restaurant_analytics.get("analytics", {})
                ctx.logger.info(f"Loaded analytics report from analytics_report.json for restaurant: {restaurant_id}")

                # Use Claude API to answer user's question with analytics context
                claude_wrapper = ClaudeWrapper()
                
                # Create prompt with analytics context
                prompt = f"""You are a restaurant analytics assistant. Analyze the following restaurant review analytics and answer the user's question.

Restaurant Analytics Data (JSON):
{json.dumps(report, indent=2)}

User Question: {user_question}

Please provide a clear, helpful answer based on the analytics data above. Be specific and reference specific metrics when relevant."""

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

# Daily review refresh
@agent.on_interval(period=REFRESH_INTERVAL_SECONDS)
async def daily_review_refresh(ctx: Context):
    """Daily review refresh task"""
    try:
        ctx.logger.info("Starting daily review refresh...")
        
        # Pull new reviews
        ctx.logger.info("Pulling new reviews...")
        #restaurant_agent.pull_reviews() #TODO: UNCOMMENT
        ctx.logger.info("Reviews pulled, checking status...")
        
        # Check snapshot status every 30 seconds until all are READY
        snapshots = restaurant_agent.database_handler.get_all_snapshots()
        ctx.logger.info(f"Total snapshots: {len(snapshots)}")
        
        while not all(snapshot.status == Status.READY.value for snapshot in snapshots):
            ctx.logger.info("Checking snapshot status...")
            snapshots_status = [{"id": s.snapshot_id, "status": s.status, "source": s.source} for s in snapshots]
            ctx.logger.info(f"Snapshot statuses: {snapshots_status}")
            
            restaurant_agent.update_pull_status()
            
            # Refresh snapshots after update
            snapshots = restaurant_agent.database_handler.get_all_snapshots()
            
            ctx.logger.info("Waiting 120 seconds before next status check...")
            await asyncio.sleep(120)
        
        ctx.logger.info("All snapshots are ready, proceeding with LLM processing...")
        
        # Process reviews with LLM
        ctx.logger.info("Starting LLM processing of reviews...")
        stats = restaurant_agent.process_reviews_with_llm()
        
        ctx.logger.info(f"LLM Processing Results:")
        ctx.logger.info(f"  Total processed: {stats['processed_count']}")
        ctx.logger.info(f"  Successful: {stats['success_count']}")
        ctx.logger.info(f"  Failed: {stats['failed_count']}")
        ctx.logger.info(f"  Total API tokens: {stats['total_tokens']}")
        
        # Generate analytics report (multi-restaurant for storage)
        ctx.logger.info("Generating analytics report...")
        try:
            report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'analytics_report.json')
            report = restaurant_agent.generate_analytics(output_path=report_path)
            ctx.logger.info(f"Analytics report generated and exported to {report_path}")
        except Exception as e:
            ctx.logger.error(f"Error generating analytics: {e}")
        
        ctx.logger.info("Daily review refresh completed successfully")
        
    except Exception as e:
        ctx.logger.error(f"Error in daily review refresh: {e}")

# Register the protocol with the agent
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    print("Starting Review Agent REST Server...")
    print("Available endpoints:")
    print("  GET /analytics - Analytics report")
    print(f"Server running on http://localhost:8003")
    print(f"Refresh interval: {REFRESH_INTERVAL_SECONDS}s (24 hours)")
    agent.run()