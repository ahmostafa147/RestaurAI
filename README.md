# RestaurAI

AI-powered restaurant operations suite with autonomous agents for inventory, menu analytics, and review monitoring.

## Structure

```
RestaurAI/
├── agents/              # AI agent services
│   ├── ingredient/      # Inventory & consumption tracking
│   ├── menu/           # Menu analytics & optimization
│   └── review/         # Review scraping & sentiment analysis
├── backend/            # Core business logic
│   ├── src/
│   │   ├── core/      # Restaurant operations (inventory, orders, tables)
│   │   ├── database/  # ChromaDB persistence
│   │   ├── models/    # Data models
│   │   └── mcp/       # MCP server (FastAPI + SSE)
│   └── tests/
├── frontend/           # React + TypeScript dashboard
├── data/              # Local data storage (ChromaDB, reports)
└── config/            # Configuration files
```

## Quick Start

### Backend (MCP Server)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run MCP server
python backend/src/mcp/http_server.py
```

Server runs on `http://127.0.0.1:8001` with SSE transport.

### Frontend (Dashboard)

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs on `http://localhost:3000`

### Agent Services

Each agent runs as an independent service:

```bash
# Ingredient Agent (http://localhost:8004)
python agents/ingredient/ingredient_agent_server.py

# Menu Agent (http://localhost:8006)
python agents/menu/menu_agent_server.py

# Review Agent (http://localhost:8003)
python agents/review/restaurant_review_agent.py
```

## Usage

```python
from backend.src.core.restaurant import Restaurant

# Create restaurant
r = Restaurant("Tony's Diner")

# Manage tables
r.reserve_table("John", 4, "7:00 PM")

# Manage inventory
from backend.src.models.ingredient import Ingredient
r.add_ingredient(Ingredient(1, "Beef", 15.0, "lbs"))

# Create and manage orders
ticket = r.create_ticket(table_number=1)
r.place_order(table_number=1, item_id=3, ticket_id=ticket["id"])
```

## Agents

### Ingredient Agent
- Real-time inventory tracking
- Consumption pattern analysis
- Predictive stock alerts
- LLM-powered reorder suggestions

**Endpoints:**
- `GET /metrics` - Dashboard metrics
- `GET /inventory_report` - Full inventory report
- `GET /low_stock` - Low stock alerts
- `GET /reorder_suggestions` - Reorder suggestions

### Menu Agent
- Menu item performance analytics
- Profit margin analysis
- Temporal ordering patterns
- LLM-powered optimization recommendations

**Endpoints:**
- `GET /menu_analytics` - Full analytics report
- `GET /popular_items` - Popular items analysis
- `GET /profit_analysis` - Profit analysis
- `GET /revenue_analysis` - Revenue metrics

### Review Agent
- Multi-platform review scraping (Yelp, Google)
- Sentiment analysis with LLM
- Customer insights & segmentation
- Staff performance tracking from reviews

## Development

### Run Tests

```bash
# Backend tests
python backend/tests/test_restaurant.py

# Agent tests
python agents/ingredient/tests/test_ingredient_agent.py
```

### Expose with ngrok

```bash
ngrok http 8001  # MCP server (http://127.0.0.1:8001)
ngrok http 8003  # Review agent (http://localhost:8003)
ngrok http 8004  # Ingredient agent (http://localhost:8004)
ngrok http 8006  # Menu agent (http://localhost:8006)
```

## Data Storage

- **ChromaDB**: Persistent restaurant data (`data/restaurant_data/`)
- **Reports**: Generated analytics (`data/*.json`)
- **Databases**: Review data (`data/database.json`)
