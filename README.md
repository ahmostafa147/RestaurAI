# RestaurAI

AI-powered restaurant operations suite with 6 autonomous agents.

## Structure

- `src/core/` - Restaurant business logic (inventory, orders, tables)
- `src/database/` - ChromaDB persistence
- `src/mcp/` - MCP server (FastAPI + SSE)
- `src/agents/` - AI agents (coming soon)
- `frontend/` - React + TypeScript dashboard
- `tests/` - Test suite
- `data/` - Local data storage

## Usage

```python
from src.core.restaurant import Restaurant

r = Restaurant("Tony's Diner")
r.reserve_table("John", 4, "7:00 PM")
```

## Quick Start

### Backend (MCP Server)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run MCP server
python src/mcp/http_server.py
```

Server runs on `http://127.0.0.1:8001` with SSE transport.

### Frontend (Dashboard)

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs on `http://localhost:3000`

## Agent Suite

- **Reservation Agent**: Bookings & table optimization
- **Inventory Agent**: Stock tracking & auto-ordering
- **Review Agent**: Monitor Yelp/Google reviews
- **Staff Agent**: Shift scheduling & swap requests
- **Menu Agent**: Sales analytics & specials optimization
- **Order Agent**: Kitchen flow & order tracking

## Expose with ngrok

```bash
ngrok http 8001
```
