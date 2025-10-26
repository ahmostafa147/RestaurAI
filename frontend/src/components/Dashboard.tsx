import { Package, Star, Users, UtensilsCrossed, ClipboardList, AlertCircle, TrendingUp } from 'lucide-react';
import { AgentCard } from './AgentCard';
import { ReservationToggle } from './ReservationToggle';
import { InventoryPanel } from './InventoryPanel';
import { ReviewPanel } from './ReviewPanel';
import { api } from '../services/api';
import { useState, useEffect } from 'react';

export function Dashboard() {
  const [inventoryMetrics, setInventoryMetrics] = useState({ lowStockItems: 0, totalItems: 0, lastUpdated: '' });
  const [reviewMetrics, setReviewMetrics] = useState({ unreadReviews: 0, averageRating: 0, flaggedIssues: 0 });
  const [showInventory, setShowInventory] = useState(false);
  const [showReviews, setShowReviews] = useState(false);

  useEffect(() => {
    const fetchMetrics = () => {
      api.getInventoryMetrics().then(setInventoryMetrics);
      api.getReviewMetrics().then(setReviewMetrics);
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Agent Overview</h2>
        <p className="text-sm text-gray-500">Manage your restaurant operations from one place</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ReservationToggle />

        <div className="relative">
          {inventoryMetrics.lowStockItems > 0 && (
            <div className="absolute -top-2 -right-2 z-10 bg-red-600 text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-lg animate-pulse">
              {inventoryMetrics.lowStockItems}
            </div>
          )}
          <AgentCard
            title="Inventory Agent"
            description="Stock tracking & auto-ordering"
            icon={Package}
            status="active"
            metrics={[
              { label: 'Low Stock', value: inventoryMetrics.lowStockItems },
              { label: 'Total Items', value: inventoryMetrics.totalItems },
              { label: 'Updated', value: inventoryMetrics.lastUpdated ? new Date(inventoryMetrics.lastUpdated).toLocaleTimeString() : '-' },
            ]}
            action={
              <button
                onClick={() => setShowInventory(true)}
                className="w-full px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-sm hover:shadow flex items-center justify-center gap-2"
              >
                {inventoryMetrics.lowStockItems > 0 && <AlertCircle className="w-4 h-4" />}
                View Inventory
              </button>
            }
          />
        </div>

        <div className="relative">
          {reviewMetrics.flaggedIssues > 0 && (
            <div className="absolute -top-2 -right-2 z-10 bg-orange-600 text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-lg animate-pulse">
              {reviewMetrics.flaggedIssues}
            </div>
          )}
          <AgentCard
            title="Review Agent"
            description="Monitor & respond to reviews"
            icon={Star}
            status="active"
            metrics={[
              { label: 'Unread', value: reviewMetrics.unreadReviews },
              { label: 'Avg Rating', value: reviewMetrics.averageRating.toFixed(1) },
              { label: 'Flagged', value: reviewMetrics.flaggedIssues },
            ]}
            action={
              <button
                onClick={() => setShowReviews(true)}
                className="w-full px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-sm hover:shadow flex items-center justify-center gap-2"
              >
                <TrendingUp className="w-4 h-4" />
                View Analytics
              </button>
            }
          />
        </div>

        <AgentCard
          title="Staff Agent"
          description="Scheduling & shift management"
          icon={Users}
          status="active"
          metrics={[
            { label: 'Active', value: 12 },
            { label: 'Shifts', value: 15 },
            { label: 'Requests', value: 3 },
          ]}
          action={
            <button className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              Manage Staff
            </button>
          }
        />

        <AgentCard
          title="Menu Agent"
          description="Optimize pricing & specials"
          icon={UtensilsCrossed}
          status="active"
          metrics={[
            { label: 'Active', value: 34 },
            { label: 'Specials', value: 3 },
            { label: 'Low Sales', value: 4 },
          ]}
          action={
            <button className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              Manage Menu
            </button>
          }
        />

        <AgentCard
          title="Order Agent"
          description="Kitchen flow & order tracking"
          icon={ClipboardList}
          status="active"
          metrics={[
            { label: 'Active', value: 7 },
            { label: 'Today', value: 23 },
            { label: 'Avg Time', value: '18m' },
          ]}
          action={
            <button className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              View Orders
            </button>
          }
        />
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="bg-green-100 p-2 rounded-lg">
              <Package className="w-5 h-5 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">Inventory Agent Active</h3>
              <p className="text-sm text-gray-600">
                Real-time inventory tracking is live.
                {inventoryMetrics.lowStockItems > 0 && (
                  <span className="block mt-1 font-medium text-red-600">
                    ⚠️ {inventoryMetrics.lowStockItems} items need attention
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="bg-purple-100 p-2 rounded-lg">
              <Star className="w-5 h-5 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-1">Review Agent Active</h3>
              <p className="text-sm text-gray-600">
                AI-powered review analytics with sentiment analysis.
                {reviewMetrics.averageRating > 0 && (
                  <span className="block mt-1 font-medium text-purple-600">
                    ⭐ {reviewMetrics.averageRating.toFixed(1)} average rating
                  </span>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {showInventory && <InventoryPanel onClose={() => setShowInventory(false)} />}
      {showReviews && <ReviewPanel onClose={() => setShowReviews(false)} />}
    </div>
  );
}
