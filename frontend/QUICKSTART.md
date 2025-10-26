# Frontend Quick Start

## Install & Run

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## What's Built

### Dashboard Layout
- Clean header with RestaurAI branding
- 6 agent cards in responsive grid (3 columns on desktop)
- Status indicators (active/idle/disabled/pending)
- Real-time metrics for each agent
- Action buttons for future deep-linking

### Agent Cards

1. **Reservation Agent** (Special Toggle)
   - On/Off button to accept/disable reservations
   - Shows: today's count, pending, total tables
   - Status changes with toggle state

2. **Inventory Agent**
   - Shows: low stock items, total items, pending orders
   - "View Inventory" action button
   - Ready for stock management integration

3. **Review Agent**
   - Shows: unread reviews, average rating, flagged issues
   - "Review Dashboard" action button
   - Ready for Yelp/Google API integration

4. **Staff Agent**
   - Shows: active staff, scheduled shifts, pending requests
   - "Manage Staff" action button
   - Ready for scheduling logic

5. **Menu Agent**
   - Shows: active items, today's specials, low performers
   - "Manage Menu" action button
   - Ready for analytics integration

6. **Order Agent**
   - Shows: active orders, completed today, avg prep time
   - "View Orders" action button
   - Ready for kitchen display integration

### Architecture

```
Components:
- Header: Logo + status indicator
- Dashboard: Main layout container
- AgentCard: Reusable card component
- ReservationToggle: Special card with toggle

Services:
- api.ts: Placeholder API methods (ready for backend)

Types:
- Full TypeScript definitions for all agents
- Status types, metrics interfaces
```

## Integration Points

All API methods in `src/services/api.ts` are placeholders marked with `// TODO`. Connect them to your MCP server endpoints:

```typescript
// Example - Update these methods:
async getInventoryMetrics(): Promise<InventoryMetrics> {
  // TODO: Replace with actual API call
  const response = await fetch('/api/inventory/metrics');
  return response.json();
}
```

## Next Steps

1. **Implement agents** in backend `/src/agents/`
2. **Create API endpoints** in MCP server
3. **Update** `frontend/src/services/api.ts` with real calls
4. **Add routing** for detail views (React Router)
5. **Real-time updates** with WebSockets/SSE
6. **Authentication** for multi-restaurant support

## Design Choices

- **Tailwind CSS**: Utility-first, easy to customize
- **Lucide Icons**: Modern, consistent icon set
- **TypeScript**: Type safety for reliability
- **Vite**: Fast dev server, optimized builds
- **Component-based**: Each agent is isolated, easy to modify

## Customization

Colors, gradients, and styling can be adjusted in:
- `tailwind.config.js` - Theme configuration
- Component files - Individual styles
- `index.css` - Global styles
