# RestaurAI

Restaurant management system with ChromaDB persistence and MCP server.

## Structure

- `src/core/` - Restaurant business logic
- `src/database/` - ChromaDB operations
- `src/mcp/` - MCP server
- `src/agents/` - AI agents (coming soon)
- `tests/` - Test files
- `data/` - Local data storage

## Usage

```python
from src.core.restaurant import Restaurant

r = Restaurant("Tony's Diner")
r.reserve_table("John", 4, "7:00 PM")
```

## Run MCP Server

```bash
python src/mcp/http_server.py
```

Runs on `http://127.0.0.1:8001` with SSE transport.

## Expose with ngrok

```bash
ngrok http 8001
```
