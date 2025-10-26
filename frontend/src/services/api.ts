import type { InventoryMetrics, ReviewMetrics, MenuMetrics } from '../types';
import { callMCPTool } from '../utils/mcpClient';

// ==================== INTERFACES ====================

export interface LowStockAlert {
  ingredient_name: string;
  current_quantity: number;
  unit: string;
  estimated_depletion_date: string;
  days_remaining: number;
  severity: string;
  recommendation: string;
}

export interface ReorderSuggestion {
  ingredient_name: string;
  current_quantity: number;
  suggested_quantity: number;
  unit: string;
  urgency: string;
  reasoning: string;
}

export interface MenuItem {
  item_id: number;
  name: string;
  category: string;
  price: number;
  popularity: {
    order_count: number;
    total_quantity: number;
  };
  financial: {
    revenue: number;
    order_count: number;
    profit_margin_percentage: number;
  };
  llm_insights?: {
    estimated_prep_time_minutes?: number;
  };
}

// ==================== API CLASS ====================

class RestaurantAPI {
  private secureKey: string | null = null;

  setSecureKey(key: string) {
    this.secureKey = key;
  }

  // ==================== MCP TOOL WRAPPERS ====================

  private async callMCPToolInternal(tool: string, args: any = {}) {
    console.log(`[API] Calling MCP tool: ${tool}`, args);
    try {
      const result = await callMCPTool(tool, args);
      console.log(`[API] MCP tool ${tool} result:`, result);
      // callMCPTool already parses JSON, so just return it
      return result;
    } catch (error) {
      console.error(`[API] MCP tool ${tool} failed:`, error);
      throw error;
    }
  }

  // ==================== AGENT API HELPERS ====================

  private async callAgentAPI(endpoint: string, params: Record<string, string> = {}) {
    const queryParams = new URLSearchParams(params);
    const url = `${endpoint}?${queryParams.toString()}`;
    const response = await fetch(url);
    const data = await response.json();
    // Agent responses are wrapped in { response: "..." } and response contains JSON string
    return typeof data.response === 'string' ? JSON.parse(data.response) : data.response;
  }

  // ==================== INVENTORY AGENT APIs ====================

  async getInventoryMetrics(): Promise<InventoryMetrics> {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/ingredient-api/metrics', {
        secure_key: this.secureKey
      });

      return {
        lowStockItems: data.lowStock?.length || 0,
        totalItems: data.totalItems || 0,
        lastUpdated: data.timestamp || new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to fetch inventory metrics:', error);
      return { lowStockItems: 0, totalItems: 0, lastUpdated: new Date().toISOString() };
    }
  }

  async getLowStockAlerts(): Promise<LowStockAlert[]> {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/ingredient-api/low_stock', {
        secure_key: this.secureKey
      });

      return data.alerts || [];
    } catch (error) {
      console.error('Failed to fetch low stock alerts:', error);
      return [];
    }
  }

  async getReorderSuggestions(): Promise<ReorderSuggestion[]> {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/ingredient-api/reorder_suggestions', {
        secure_key: this.secureKey
      });

      return data.suggestions || [];
    } catch (error) {
      console.error('Failed to fetch reorder suggestions:', error);
      return [];
    }
  }

  async getConsumptionAnalysis() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      return await this.callAgentAPI('/ingredient-api/consumption_analysis', {
        secure_key: this.secureKey
      });
    } catch (error) {
      console.error('Failed to fetch consumption analysis:', error);
      return null;
    }
  }

  async getUsageSummary() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      return await this.callAgentAPI('/ingredient-api/usage_summary', {
        secure_key: this.secureKey
      });
    } catch (error) {
      console.error('Failed to fetch usage summary:', error);
      return null;
    }
  }

  async getInventoryReport() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      return await this.callAgentAPI('/ingredient-api/inventory_report', {
        secure_key: this.secureKey
      });
    } catch (error) {
      console.error('Failed to fetch inventory report:', error);
      return null;
    }
  }

  // ==================== MENU AGENT APIs ====================

  async getMenuMetrics(): Promise<MenuMetrics> {
    try {
      if (!this.secureKey) {
        console.warn('[API] No secure key for menu metrics');
        throw new Error('No secure key');
      }

      console.log('[API] Fetching menu metrics...');

      // Try to get analytics from Menu Agent first
      try {
        const analytics = await this.callAgentAPI('/menu-api/menu_analytics', {
          secure_key: this.secureKey
        });

        console.log('[API] Menu analytics from agent:', analytics);

        if (analytics && analytics.menu_items && analytics.menu_items.length > 0) {
          // Calculate metrics from the menu data
          const menuItems = analytics.menu_items || [];
          const summary = analytics.summary_metrics || {};

          // Find top performers and low performers
          const sortedByOrders = [...menuItems].sort((a: any, b: any) =>
            (b.popularity?.order_count || 0) - (a.popularity?.order_count || 0)
          );

          const topPerformers = sortedByOrders.slice(0, 3).length;
          const lowPerformers = sortedByOrders.slice(-3).filter((item: any) =>
            (item.popularity?.order_count || 0) < (summary.total_orders || 0) / menuItems.length
          ).length;

          console.log('[API] Returning agent-based metrics:', {
            activeItems: summary.total_menu_items || menuItems.length,
            specialsToday: topPerformers,
            lowPerformers: lowPerformers
          });

          return {
            activeItems: summary.total_menu_items || menuItems.length || 0,
            specialsToday: topPerformers,
            lowPerformers: lowPerformers
          };
        }
      } catch (agentError) {
        console.warn('[API] Menu agent not available, falling back to MCP data:', agentError);
      }

      // Fallback: Use MCP menu data
      console.log('[API] Using MCP fallback for menu metrics');
      const menuData = await this.getMenu();
      console.log('[API] Menu data from MCP:', menuData);

      const menuItems = menuData?.menu_items || [];

      const fallbackMetrics = {
        activeItems: menuItems.length,
        specialsToday: 0,
        lowPerformers: 0
      };

      console.log('[API] Returning MCP-based metrics:', fallbackMetrics);
      return fallbackMetrics;
    } catch (error) {
      console.error('[API] Failed to fetch menu metrics:', error);
      return { activeItems: 0, specialsToday: 0, lowPerformers: 0 };
    }
  }

  async getMenuAnalytics() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/menu-api/menu_analytics', {
        secure_key: this.secureKey
      });

      return data;
    } catch (error) {
      console.error('Failed to fetch menu analytics:', error);
      return null;
    }
  }

  async getPopularItems() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/menu-api/popular_items', {
        secure_key: this.secureKey
      });

      // Data contains menu_items and overall_insights
      return data;
    } catch (error) {
      console.error('Failed to fetch popular items:', error);
      return null;
    }
  }

  async getProfitAnalysis() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/menu-api/profit_analysis', {
        secure_key: this.secureKey
      });

      return data;
    } catch (error) {
      console.error('Failed to fetch profit analysis:', error);
      return null;
    }
  }

  async getMenuRecommendations() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      const data = await this.callAgentAPI('/menu-api/menu_recommendations', {
        secure_key: this.secureKey
      });

      return data;
    } catch (error) {
      console.error('Failed to fetch menu recommendations:', error);
      return null;
    }
  }

  async getRevenueAnalysis() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      return await this.callAgentAPI('/menu-api/revenue_analysis', {
        secure_key: this.secureKey
      });
    } catch (error) {
      console.error('Failed to fetch revenue analysis:', error);
      return null;
    }
  }

  async getMenuPerformance() {
    try {
      if (!this.secureKey) throw new Error('No secure key');

      return await this.callAgentAPI('/menu-api/menu_performance', {
        secure_key: this.secureKey
      });
    } catch (error) {
      console.error('Failed to fetch menu performance:', error);
      return null;
    }
  }

  // ==================== REVIEW AGENT APIs ====================

  async getReviewMetrics(): Promise<ReviewMetrics> {
    try {
      const analytics = await this.getReviewAnalytics();
      if (!analytics) {
        return { unreadReviews: 0, averageRating: 0, flaggedIssues: 0 };
      }

      // Safely access nested properties with optional chaining
      const flaggedCount = Object.values(analytics.reputation_insights?.anomaly_flags || {}).reduce((sum: number, val: any) => sum + (val || 0), 0) as number;
      const totalReviews = analytics.metadata?.total_reviews || 0;
      const processedReviews = analytics.metadata?.processed_reviews || 0;
      const unprocessed = totalReviews - processedReviews;

      return {
        unreadReviews: unprocessed,
        averageRating: analytics.basic_metrics?.overall_performance?.average_rating || 0,
        flaggedIssues: flaggedCount
      };
    } catch (error) {
      console.error('Failed to fetch review metrics:', error);
      return { unreadReviews: 0, averageRating: 0, flaggedIssues: 0 };
    }
  }

  async getReviewAnalytics() {
    try {
      const response = await fetch('/review-api/analytics');
      if (!response.ok) {
        console.warn('Review API returned non-OK status:', response.status);
        return null;
      }
      const data = await response.json();
      if (!data || !data.response) {
        console.warn('Review API returned empty or invalid data');
        return null;
      }
      return JSON.parse(data.response);
    } catch (error) {
      console.error('Failed to fetch review analytics:', error);
      return null;
    }
  }

  // ==================== MCP TOOL WRAPPERS ====================

  async getMenu() {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('get_menu', { key: this.secureKey });
  }

  async getReservations() {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('get_reservations', { key: this.secureKey });
  }

  async getOrders() {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('get_orders', { key: this.secureKey });
  }

  async reserveTable(name: string, partySize: number, time: string) {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('reserve_table', {
      key: this.secureKey,
      name,
      party_size: partySize,
      time
    });
  }

  async placeOrder(tableNumber: number, itemIds: number[]) {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('place_order', {
      key: this.secureKey,
      table_number: tableNumber,
      item_ids: itemIds
    });
  }

  async seatParty(tableNumber: number) {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('seat_party', {
      key: this.secureKey,
      table_number: tableNumber
    });
  }

  async clearTable(tableNumber: number) {
    if (!this.secureKey) throw new Error('No secure key');
    return await this.callMCPToolInternal('clear_table', {
      key: this.secureKey,
      table_number: tableNumber
    });
  }
}

export const api = new RestaurantAPI();
