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
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.json')

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
            restaurant_ids = list(restaurant_agent.database_handler.get_all_restaurant_ids())
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
        
        # Step 3: Extract restaurant_id from message content
        restaurant_id = None
        if hasattr(msg, 'content') and msg.content:
            for content in msg.content:
                if hasattr(content, 'text'):
                    # Try to parse restaurant_id from message text
                    # Look for patterns like "restaurant_id: causwells-sf" or just "causwells-sf"
                    text = content.text.strip()
                    if 'restaurant_id:' in text:
                        restaurant_id = text.split('restaurant_id:')[1].strip()
                    elif text and not text.startswith('{') and not text.startswith('['):
                        # Assume the entire message is the restaurant_id if it's not JSON
                        restaurant_id = text
        
        if not restaurant_id:
            response = "Error: restaurant_id is required. Please provide a restaurant ID in your message."
            ctx.logger.warning("No restaurant_id provided in message")
        else:
            # Step 4: Generate analytics for specific restaurant
            try:
                from analytics.analytics_engine import AnalyticsEngine
                engine = AnalyticsEngine(restaurant_agent.database_handler)
                report = engine.generate_full_report(restaurant_id=restaurant_id)
                response = json.dumps(report, indent=2)
                ctx.logger.info(f"Analytics report generated for restaurant: {restaurant_id}")
                
            except Exception as e:
                response = f"Error generating analytics for restaurant {restaurant_id}: {str(e)}"
                ctx.logger.error(f"Error generating analytics for restaurant {restaurant_id}: {e}")
        
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
        # restaurant_agent.pull_reviews() #TODO: UNCOMMENT
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
            
            ctx.logger.info("Waiting 30 seconds before next status check...")
            await asyncio.sleep(30)
        
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
            report = restaurant_agent.generate_analytics(output_path="analytics_report.json")
            ctx.logger.info("Analytics report generated and exported to analytics_report.json")
        except Exception as e:
            ctx.logger.error(f"Error generating analytics: {e}")
        
        ctx.logger.info("Daily review refresh completed successfully")
        
    except Exception as e:
        ctx.logger.error(f"Error in daily review refresh: {e}")

# Register the protocol with the agent
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()