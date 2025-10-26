# RestaurAI Frontend

Modern React + TypeScript dashboard for restaurant operations management.

## Features

- **Agent Dashboard**: Manage all 6 restaurant operation agents from one interface
- **Real-time Status**: Monitor agent activity and metrics
- **Reservation Toggle**: Quick on/off control for accepting reservations
- **Responsive Design**: Works on desktop and mobile devices
- **Type-Safe**: Built with TypeScript for reliability

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

The app will run on `http://localhost:3000`

## Architecture

```
src/
├── components/       # React components
│   ├── Header.tsx
│   ├── Dashboard.tsx
│   ├── AgentCard.tsx
│   └── ReservationToggle.tsx
├── services/         # API integration layer
│   └── api.ts
├── types/            # TypeScript definitions
│   └── index.ts
├── App.tsx           # Main app component
└── main.tsx          # Entry point
```

## Agent Integration

Each agent card is a separate module ready for backend integration:

- **Reservation Agent**: Booking management with toggle control
- **Inventory Agent**: Stock tracking and auto-ordering
- **Review Agent**: Customer feedback monitoring
- **Staff Agent**: Scheduling and shift management
- **Menu Agent**: Menu optimization and specials
- **Order Agent**: Kitchen flow and order tracking

## Development

Backend API calls are defined in `src/services/api.ts` with placeholder implementations. Once backend agents are ready, update these methods to call the actual MCP server endpoints.

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide Icons
