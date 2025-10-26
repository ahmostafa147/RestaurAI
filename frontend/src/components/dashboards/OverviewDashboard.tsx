import { useState, useEffect } from 'react';
import { Package, UtensilsCrossed, Star, TrendingUp, AlertCircle, Sparkles, Activity } from 'lucide-react';
import { api } from '../../services/api';

export function OverviewDashboard() {
  const [inventoryMetrics, setInventoryMetrics] = useState({ lowStockItems: 0, totalItems: 0, lastUpdated: '' });
  const [menuMetrics, setMenuMetrics] = useState({ activeItems: 0, specialsToday: 0, lowPerformers: 0 });
  const [reviewMetrics, setReviewMetrics] = useState({ unreadReviews: 0, averageRating: 0, flaggedIssues: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllMetrics();
    const interval = setInterval(fetchAllMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllMetrics = async () => {
    try {
      const [inventory, menu, review] = await Promise.all([
        api.getInventoryMetrics(),
        api.getMenuMetrics(),
        api.getReviewMetrics()
      ]);

      console.log('[Dashboard] Inventory metrics:', inventory);
      console.log('[Dashboard] Menu metrics:', menu);
      console.log('[Dashboard] Review metrics:', review);

      setInventoryMetrics(inventory);
      setMenuMetrics(menu);
      setReviewMetrics(review);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const agentCards = [
    {
      title: 'Inventory Agent',
      description: 'Stock tracking & consumption analysis',
      icon: Package,
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
      metrics: [
        { label: 'Total Items', value: inventoryMetrics.totalItems, icon: Activity },
        { label: 'Low Stock', value: inventoryMetrics.lowStockItems, icon: AlertCircle, alert: inventoryMetrics.lowStockItems > 0 },
      ],
      status: 'active'
    },
    {
      title: 'Menu Agent',
      description: 'Performance analytics & optimization',
      icon: UtensilsCrossed,
      gradient: 'from-orange-500 to-amber-500',
      bgGradient: 'from-orange-50 to-amber-50',
      metrics: [
        { label: 'Active Items', value: menuMetrics.activeItems, icon: Activity },
        { label: 'Top Performers', value: menuMetrics.specialsToday, icon: TrendingUp },
      ],
      status: 'active'
    },
    {
      title: 'Review Agent',
      description: 'Sentiment analysis & customer insights',
      icon: Star,
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50',
      metrics: [
        { label: 'Avg Rating', value: reviewMetrics.averageRating.toFixed(1), icon: Star },
        { label: 'Flagged Issues', value: reviewMetrics.flaggedIssues, icon: AlertCircle, alert: reviewMetrics.flaggedIssues > 0 },
      ],
      status: 'active'
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-8 h-8" />
            <h1 className="text-3xl font-bold">AI-Powered Restaurant Operations</h1>
          </div>
          <p className="text-white/90 text-lg mb-6">
            Your intelligent agents are monitoring inventory, menu performance, and customer reviews in real-time.
          </p>
          <div className="flex gap-4 flex-wrap">
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
              <div className="text-sm text-white/80">Last Updated</div>
              <div className="font-semibold">
                {inventoryMetrics.lastUpdated ? new Date(inventoryMetrics.lastUpdated).toLocaleTimeString() : '-'}
              </div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
              <div className="text-sm text-white/80">System Status</div>
              <div className="font-semibold flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                All Systems Active
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {agentCards.map((agent) => {
          const Icon = agent.icon;

          return (
            <div
              key={agent.title}
              className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group"
            >
              {/* Header */}
              <div className={`bg-gradient-to-r ${agent.gradient} p-6`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl group-hover:scale-110 transition-transform duration-300">
                    <Icon className="w-8 h-8 text-white" />
                  </div>
                  <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs font-semibold text-white uppercase">Active</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-1">{agent.title}</h3>
                <p className="text-white/80 text-sm">{agent.description}</p>
              </div>

              {/* Metrics */}
              <div className={`bg-gradient-to-br ${agent.bgGradient} p-6`}>
                <div className="space-y-4">
                  {agent.metrics.map((metric) => {
                    const MetricIcon = metric.icon;

                    return (
                      <div key={metric.label} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${metric.alert ? 'bg-red-100' : 'bg-white'}`}>
                            <MetricIcon className={`w-4 h-4 ${metric.alert ? 'text-red-600' : 'text-gray-600'}`} />
                          </div>
                          <span className="text-sm font-medium text-gray-700">{metric.label}</span>
                        </div>
                        <span className={`text-lg font-bold ${metric.alert ? 'text-red-600' : 'text-gray-900'}`}>
                          {metric.value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Inventory Alert */}
        {inventoryMetrics.lowStockItems > 0 && (
          <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="bg-red-100 p-3 rounded-xl">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Low Stock Alert</h3>
                <p className="text-gray-600 mb-4">
                  {inventoryMetrics.lowStockItems} items are running low and need attention
                </p>
                <button className="px-4 py-2 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg hover:from-red-700 hover:to-orange-700 transition-all duration-200 font-medium text-sm">
                  View Details
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Review Insights */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-2xl p-6">
          <div className="flex items-start gap-4">
            <div className="bg-purple-100 p-3 rounded-xl">
              <Star className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Customer Satisfaction</h3>
              <div className="flex items-baseline gap-2 mb-4">
                <span className="text-3xl font-bold text-purple-600">
                  {reviewMetrics.averageRating.toFixed(1)}
                </span>
                <span className="text-gray-600">out of 5.0</span>
              </div>
              <p className="text-sm text-gray-600">
                {reviewMetrics.averageRating >= 4.0 ? 'Excellent performance! ' : 'Room for improvement. '}
                Keep monitoring customer feedback
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
