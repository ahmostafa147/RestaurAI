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
    try {
      const res = await fetch('/ingredient-api/metrics');
      const data = await res.json();
      const metrics = JSON.parse(data.response);

      return {
        lowStockItems: metrics.lowStock?.length || 0,
        totalItems: metrics.totalItems || 0,
        lastUpdated: metrics.timestamp || new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to fetch inventory metrics:', error);
      return { lowStockItems: 0, totalItems: 0, lastUpdated: new Date().toISOString() };
    }
  }

  async getReviewMetrics(): Promise<ReviewMetrics> {
    try {
      const res = await fetch('/review-api/analytics');
      const data = await res.json();
      const analytics = JSON.parse(data.response);

      const flaggedCount = analytics.reputation_insights?.anomaly_flags?.health_safety_concern || 0;
      const unprocessed = analytics.metadata.total_reviews - analytics.metadata.processed_reviews;

      return {
        unreadReviews: unprocessed,
        averageRating: analytics.basic_metrics.overall_performance.average_rating || 0,
        flaggedIssues: flaggedCount
      };
    } catch (error) {
      console.error('Failed to fetch review metrics:', error);
      return { unreadReviews: 0, averageRating: 0, flaggedIssues: 0 };
    }
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
    try {
      const res = await fetch('/menu-api/metrics');
      const data = await res.json();
      const metrics = JSON.parse(data.response);

      return {
        activeItems: metrics.activeItems || 0,
        specialsToday: metrics.topPerformers?.length || 0,
        lowPerformers: metrics.lowPerformers?.length || 0
      };
    } catch (error) {
      console.error('Failed to fetch menu metrics:', error);
      return { activeItems: 0, specialsToday: 0, lowPerformers: 0 };
    }
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
