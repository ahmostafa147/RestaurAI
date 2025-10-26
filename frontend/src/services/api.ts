import type { ReservationState, InventoryMetrics, ReviewMetrics, StaffMetrics, MenuMetrics, OrderMetrics } from '../types';

const API_BASE = '/api';

// Placeholder API service - will connect to MCP server once agents are implemented
class RestaurantAPI {
  async getReservationState(): Promise<ReservationState> {
    // TODO: Connect to backend reservation agent
    return {
      enabled: true,
      todayCount: 12,
      pendingCount: 3
    };
  }

  async toggleReservations(enabled: boolean): Promise<void> {
    // TODO: POST to /api/reservations/toggle
    console.log('Toggle reservations:', enabled);
  }

  async getInventoryMetrics(): Promise<InventoryMetrics> {
    // TODO: Connect to inventory agent
    return {
      lowStockItems: 5,
      totalItems: 47,
      lastUpdated: new Date().toISOString()
    };
  }

  async getReviewMetrics(): Promise<ReviewMetrics> {
    // TODO: Connect to review agent
    return {
      unreadReviews: 8,
      averageRating: 4.3,
      flaggedIssues: 2
    };
  }

  async getStaffMetrics(): Promise<StaffMetrics> {
    // TODO: Connect to staff agent
    return {
      activeStaff: 12,
      scheduledShifts: 15,
      pendingRequests: 3
    };
  }

  async getMenuMetrics(): Promise<MenuMetrics> {
    // TODO: Connect to menu agent
    return {
      activeItems: 34,
      specialsToday: 3,
      lowPerformers: 4
    };
  }

  async getOrderMetrics(): Promise<OrderMetrics> {
    // TODO: Connect to order manager
    return {
      activeOrders: 7,
      completedToday: 23,
      avgPrepTime: '18m'
    };
  }
}

export const api = new RestaurantAPI();
