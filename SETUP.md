# Restaurant Review API Setup Guide

## Overview
This setup creates a FastAPI service that processes restaurant reviews and an external uAgent that calls the API periodically.

## Architecture
- **FastAPI Service** (`review_agent/restaurant_review_agent.py`): Runs locally, exposes REST endpoints
- **External uAgent** (`external_agent.py`): Deployed to AgentVerse, calls the API hourly
- **ngrok**: Exposes local FastAPI service to the internet

## Setup Steps

### 1. Install Dependencies
```bash
cd review_agent
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
# For the FastAPI service
export API_KEY="your-secure-api-key-here"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For the external agent (will be set in AgentVerse)
export API_BASE_URL="https://your-ngrok-url.ngrok.io"
export API_KEY="your-secure-api-key-here"
```

### 3. Run the FastAPI Service
```bash
cd review_agent
python restaurant_review_agent.py
```
The service will start on `http://localhost:8000`

### 4. Expose with ngrok
In a new terminal:
```bash
ngrok http 8000
```
Copy the public URL (e.g., `https://abc123.ngrok.io`)

### 5. Deploy External Agent to AgentVerse
1. Upload `external_agent.py` to AgentVerse
2. Set environment variables in AgentVerse:
   - `API_BASE_URL` = your ngrok URL
   - `API_KEY` = same key as FastAPI service
3. Deploy the agent

## API Endpoints

### Authentication
All endpoints require `X-API-Key` header with your API key.

### Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/trigger-pull` - Trigger review processing
- `GET /api/status` - Get current status
- `GET /api/analytics` - Get analytics report

### Example Usage
```bash
# Trigger review pull
curl -X POST "https://your-ngrok-url.ngrok.io/api/trigger-pull" \
  -H "X-API-Key: your-api-key"

# Get status
curl -X GET "https://your-ngrok-url.ngrok.io/api/status" \
  -H "X-API-Key: your-api-key"

# Get analytics
curl -X GET "https://your-ngrok-url.ngrok.io/api/analytics" \
  -H "X-API-Key: your-api-key"
```

## How It Works

1. **External Agent** runs on AgentVerse and calls the API every hour
2. **API Service** receives the trigger and starts background processing:
   - Pulls new reviews from Google/Yelp
   - Waits for snapshots to be ready
   - Processes reviews with LLM
   - Generates analytics report
3. **External Agent** monitors status and retrieves analytics

## Database
- Uses `review_agent/database.json` for data storage
- Never clears existing data, only appends new reviews

## Troubleshooting

### FastAPI Service Issues
- Check that all dependencies are installed
- Verify API_KEY environment variable is set
- Check logs for specific error messages

### ngrok Issues
- Ensure ngrok is installed and authenticated
- Check that port 8000 is not blocked
- Verify the public URL is accessible

### External Agent Issues
- Verify API_BASE_URL points to your ngrok URL
- Check that API_KEY matches between service and agent
- Monitor AgentVerse logs for connection issues

## Production Considerations

For production deployment, consider:
- Using a cloud hosting service (Railway, Render, etc.) instead of ngrok
- Implementing proper database (PostgreSQL, MongoDB) instead of JSON file
- Adding rate limiting and more robust authentication
- Setting up monitoring and alerting
