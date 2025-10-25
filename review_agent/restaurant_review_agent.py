"""
Restaurant Review API Service
FastAPI service that exposes REST endpoints for review processing and analytics.
"""

import sys
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from main import RestaurantReviewAgent
from scrapers.pull_dataset import Status

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant Review API",
    description="API for restaurant review processing and analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("API_KEY", "default-api-key")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.json')

# Initialize the restaurant review agent
restaurant_agent = RestaurantReviewAgent(DATABASE_PATH)

# Pydantic models for API responses
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class StatusResponse(BaseModel):
    total_reviews: int
    processed_reviews: int
    snapshots_count: int
    snapshots_status: list
    last_updated: Optional[str] = None

class AnalyticsResponse(BaseModel):
    report: Dict[str, Any]
    generated_at: str

# Authentication dependency
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Background task for review processing
async def process_reviews_background():
    """Background task to process reviews"""
    try:
        logger.info("Starting background review processing...")
        
        # Pull new reviews
        logger.info("Pulling new reviews...")
        restaurant_agent.pull_reviews()
        logger.info("Reviews pulled, checking status...")
        
        # Check snapshot status every 10 seconds until all are READY
        snapshots = restaurant_agent.database_handler.get_all_snapshots()
        logger.info(f"Total snapshots: {len(snapshots)}")
        
        while not all(snapshot.status == Status.READY.value for snapshot in snapshots):
            logger.info("Checking snapshot status...")
            snapshots_status = [{"id": s.snapshot_id, "status": s.status, "source": s.source} for s in snapshots]
            logger.info(f"Snapshot statuses: {snapshots_status}")
            
            restaurant_agent.update_pull_status()
            
            # Refresh snapshots after update
            snapshots = restaurant_agent.database_handler.get_all_snapshots()
            
            logger.info("Waiting 10 seconds before next status check...")
            await asyncio.sleep(10)
        
        logger.info("All snapshots are ready, proceeding with LLM processing...")
        
        # Process reviews with LLM
        logger.info("Starting LLM processing of reviews...")
        stats = restaurant_agent.process_reviews_with_llm()
        
        logger.info(f"LLM Processing Results:")
        logger.info(f"  Total processed: {stats['processed_count']}")
        logger.info(f"  Successful: {stats['success_count']}")
        logger.info(f"  Failed: {stats['failed_count']}")
        logger.info(f"  Total API tokens: {stats['total_tokens']}")
        
        # Generate analytics report
        logger.info("Generating analytics report...")
        try:
            report = restaurant_agent.generate_analytics(output_path="analytics_report.json")
            logger.info("Analytics report generated and exported to analytics_report.json")
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
        
        logger.info("Background review processing completed.")
        
    except Exception as e:
        logger.error(f"Error in background review processing: {e}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Restaurant Review API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/trigger-pull")
async def trigger_pull(background_tasks: BackgroundTasks, api_key: str = Depends(verify_api_key)):
    """Trigger review pulling and processing"""
    try:
        logger.info("Triggering review pull via API...")
        
        # Add background task
        background_tasks.add_task(process_reviews_background)
        
        return APIResponse(
            success=True,
            message="Review processing started in background",
            data={"status": "processing"}
        )
        
    except Exception as e:
        logger.error(f"Error triggering review pull: {e}")
        raise HTTPException(status_code=500, detail=f"Error triggering review pull: {str(e)}")

@app.get("/api/status")
async def get_status(api_key: str = Depends(verify_api_key)):
    """Get current review processing status"""
    try:
        logger.info("Getting status via API...")
        
        # Get current status
        all_reviews = restaurant_agent.database_handler.get_all_reviews()
        processed_reviews = [r for r in all_reviews if r.llm_processed]
        snapshots = restaurant_agent.database_handler.get_all_snapshots()
        
        snapshots_status = [{"id": s.snapshot_id, "status": s.status, "source": s.source} for s in snapshots]
        
        return StatusResponse(
            total_reviews=len(all_reviews),
            processed_reviews=len(processed_reviews),
            snapshots_count=len(snapshots),
            snapshots_status=snapshots_status,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(api_key: str = Depends(verify_api_key)):
    """Get analytics report"""
    try:
        logger.info("Generating analytics via API...")
        
        # Generate fresh analytics report
        report = restaurant_agent.generate_analytics()
        
        return AnalyticsResponse(
            report=report,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)