export type AgentStatus = 'active' | 'idle' | 'disabled' | 'pending';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  icon: string;
  metrics?: Record<string, string | number>;
}

export interface ReservationState {
  enabled: boolean;
  todayCount: number;
  pendingCount: number;
}

export interface InventoryMetrics {
  lowStockItems: number;
  totalItems: number;
  lastUpdated: string;
}

export interface ReviewMetrics {
  unreadReviews: number;
  averageRating: number;
  flaggedIssues: number;
}

export interface StaffMetrics {
  activeStaff: number;
  scheduledShifts: number;
  pendingRequests: number;
}

export interface MenuMetrics {
  activeItems: number;
  specialsToday: number;
  lowPerformers: number;
}

export interface OrderMetrics {
  activeOrders: number;
  completedToday: number;
  avgPrepTime: string;
}
