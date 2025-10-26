import { useState, useEffect } from 'react';
import { AlertTriangle, Package, Sparkles, RefreshCw, Clock, ShoppingCart, TrendingUp, ChevronDown, ChevronUp, BarChart3 } from 'lucide-react';
import { api, LowStockAlert, ReorderSuggestion } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function InventoryDashboard() {
  const [lowStockAlerts, setLowStockAlerts] = useState<LowStockAlert[]>([]);
  const [reorderSuggestions, setReorderSuggestions] = useState<ReorderSuggestion[]>([]);
  const [consumptionAnalysis, setConsumptionAnalysis] = useState<any>(null);
  const [usageSummary, setUsageSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showConsumption, setShowConsumption] = useState(false);
  const [showUsage, setShowUsage] = useState(false);

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const fetchInventoryData = async () => {
    try {
      setRefreshing(true);
      const [alerts, suggestions, consumption, usage] = await Promise.all([
        api.getLowStockAlerts(),
        api.getReorderSuggestions(),
        api.getConsumptionAnalysis(),
        api.getUsageSummary()
      ]);

      console.log('[Inventory] Low stock alerts:', alerts);
      console.log('[Inventory] Reorder suggestions:', suggestions);
      console.log('[Inventory] Consumption analysis:', consumption);
      console.log('[Inventory] Usage summary:', usage);

      setLowStockAlerts(alerts);
      setReorderSuggestions(suggestions);
      setConsumptionAnalysis(consumption);
      setUsageSummary(usage);
    } catch (error) {
      console.error('Failed to fetch inventory data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'immediate': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-green-600 bg-green-50';
    }
  };

  const getChartColor = (days: number) => {
    if (days <= 2) return '#dc2626'; // red
    if (days <= 5) return '#ea580c'; // orange
    if (days <= 7) return '#f59e0b'; // amber
    return '#3b82f6'; // blue
  };

  const chartData = lowStockAlerts.map(alert => ({
    name: alert.ingredient_name.length > 15
      ? alert.ingredient_name.substring(0, 15) + '...'
      : alert.ingredient_name,
    days: alert.days_remaining,
    fullName: alert.ingredient_name
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading inventory data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <button
              onClick={fetchInventoryData}
              disabled={refreshing}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-2 rounded-lg transition-all"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="text-4xl font-bold mb-2">{lowStockAlerts.length}</div>
          <div className="text-white/90">Low Stock Alerts</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <ShoppingCart className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">{reorderSuggestions.length}</div>
          <div className="text-white/90">Reorder Suggestions</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">AI</div>
          <div className="text-white/90">Powered Analytics</div>
        </div>
      </div>

      {/* Low Stock Visualization */}
      {lowStockAlerts.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Clock className="w-6 h-6 text-blue-600" />
            Days Until Stock Depletion
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="name"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fill: '#666', fontSize: 12 }}
              />
              <YAxis tick={{ fill: '#666' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '12px'
                }}
                labelStyle={{ fontWeight: 'bold' }}
                formatter={(value: any) => [`${value} days`, 'Days Remaining']}
              />
              <Bar dataKey="days" radius={[8, 8, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getChartColor(entry.days)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Low Stock Alerts */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-red-600" />
          Critical Stock Alerts
        </h3>

        {lowStockAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">All stock levels are healthy!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {lowStockAlerts.map((alert, index) => (
              <div
                key={index}
                className={`border-2 rounded-xl p-5 ${getSeverityColor(alert.severity)} transition-all hover:shadow-md`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-lg text-gray-900">{alert.ingredient_name}</h4>
                    <div className="flex items-center gap-4 mt-2 text-sm">
                      <span className="font-semibold">
                        Current: {alert.current_quantity} {alert.unit}
                      </span>
                      <span className={`px-3 py-1 rounded-full font-semibold uppercase text-xs ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-gray-900">{alert.days_remaining}</div>
                    <div className="text-sm text-gray-600">days left</div>
                  </div>
                </div>

                <div className="bg-white/60 rounded-lg p-3 mt-3">
                  <div className="text-sm text-gray-700">
                    <strong>Estimated Depletion:</strong>{' '}
                    {new Date(alert.estimated_depletion_date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                  <div className="text-sm text-gray-700 mt-2">
                    <strong>Recommendation:</strong> {alert.recommendation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Reorder Suggestions */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-600" />
          AI-Powered Reorder Suggestions
        </h3>

        {reorderSuggestions.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No reorder suggestions at this time</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {reorderSuggestions.map((suggestion, index) => (
              <div
                key={index}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-purple-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-bold text-lg text-gray-900">{suggestion.ingredient_name}</h4>
                  <span className={`px-3 py-1 rounded-full font-semibold uppercase text-xs ${getUrgencyColor(suggestion.urgency)}`}>
                    {suggestion.urgency}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-gray-600 mb-1">Current Stock</div>
                    <div className="text-xl font-bold text-gray-900">
                      {suggestion.current_quantity} {suggestion.unit}
                    </div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-xs text-purple-600 mb-1">Suggested Order</div>
                    <div className="text-xl font-bold text-purple-600">
                      {suggestion.suggested_quantity} {suggestion.unit}
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-3">
                  <div className="text-sm text-gray-700">
                    <strong className="text-purple-600">AI Reasoning:</strong>
                    <p className="mt-1">{suggestion.reasoning}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Consumption Analysis Section */}
      {consumptionAnalysis && (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <button
            onClick={() => setShowConsumption(!showConsumption)}
            className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-3 rounded-xl text-white">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div className="text-left">
                <h3 className="text-xl font-bold text-gray-900">Consumption Analysis</h3>
                <p className="text-sm text-gray-600">Detailed ingredient consumption patterns and trends</p>
              </div>
            </div>
            {showConsumption ? (
              <ChevronUp className="w-6 h-6 text-gray-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-gray-400" />
            )}
          </button>

          {showConsumption && (
            <div className="p-6 pt-0 space-y-6 border-t border-gray-100">
              {consumptionAnalysis.trending_items && consumptionAnalysis.trending_items.length > 0 && (
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-4">Trending Items</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {consumptionAnalysis.trending_items.map((item: any, idx: number) => (
                      <div key={idx} className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 border-2 border-green-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-bold text-gray-900">{item.ingredient_name || item.name}</h5>
                            <p className="text-sm text-gray-600 mt-1">
                              {item.trend || item.description || 'Consumption increasing'}
                            </p>
                          </div>
                          <TrendingUp className="w-8 h-8 text-green-600" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {consumptionAnalysis.insights && (
                <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
                  <h4 className="font-bold text-lg text-blue-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    AI Insights
                  </h4>
                  <p className="text-gray-700 whitespace-pre-line">{consumptionAnalysis.insights}</p>
                </div>
              )}

              {consumptionAnalysis.summary && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <h4 className="font-bold text-lg text-gray-900 mb-3">Summary</h4>
                  <p className="text-gray-700">{consumptionAnalysis.summary}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Usage Summary Section */}
      {usageSummary && (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <button
            onClick={() => setShowUsage(!showUsage)}
            className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-indigo-500 to-purple-500 p-3 rounded-xl text-white">
                <BarChart3 className="w-6 h-6" />
              </div>
              <div className="text-left">
                <h3 className="text-xl font-bold text-gray-900">Usage Summary</h3>
                <p className="text-sm text-gray-600">Overall inventory usage statistics and patterns</p>
              </div>
            </div>
            {showUsage ? (
              <ChevronUp className="w-6 h-6 text-gray-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-gray-400" />
            )}
          </button>

          {showUsage && (
            <div className="p-6 pt-0 space-y-6 border-t border-gray-100">
              {usageSummary.total_items && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-indigo-50 rounded-xl p-4 border-2 border-indigo-200">
                    <div className="text-3xl font-bold text-indigo-600">{usageSummary.total_items}</div>
                    <div className="text-sm text-gray-600 mt-1">Total Items</div>
                  </div>
                  {usageSummary.low_stock_count !== undefined && (
                    <div className="bg-red-50 rounded-xl p-4 border-2 border-red-200">
                      <div className="text-3xl font-bold text-red-600">{usageSummary.low_stock_count}</div>
                      <div className="text-sm text-gray-600 mt-1">Low Stock</div>
                    </div>
                  )}
                  {usageSummary.healthy_stock_count !== undefined && (
                    <div className="bg-green-50 rounded-xl p-4 border-2 border-green-200">
                      <div className="text-3xl font-bold text-green-600">{usageSummary.healthy_stock_count}</div>
                      <div className="text-sm text-gray-600 mt-1">Healthy Stock</div>
                    </div>
                  )}
                  {usageSummary.total_value !== undefined && (
                    <div className="bg-purple-50 rounded-xl p-4 border-2 border-purple-200">
                      <div className="text-3xl font-bold text-purple-600">
                        ${typeof usageSummary.total_value === 'number' ? usageSummary.total_value.toFixed(0) : usageSummary.total_value}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">Total Value</div>
                    </div>
                  )}
                </div>
              )}

              {usageSummary.top_consumed && usageSummary.top_consumed.length > 0 && (
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-4">Most Consumed Ingredients</h4>
                  <div className="space-y-3">
                    {usageSummary.top_consumed.map((item: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-4 bg-gray-50 rounded-xl p-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold">
                          {idx + 1}
                        </div>
                        <div className="flex-grow">
                          <div className="font-semibold text-gray-900">{item.name || item.ingredient_name}</div>
                          {item.quantity && <div className="text-sm text-gray-600">Used: {item.quantity} {item.unit || ''}</div>}
                        </div>
                        {item.percentage && (
                          <div className="text-right">
                            <div className="text-lg font-bold text-indigo-600">{item.percentage}%</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {usageSummary.recommendations && (
                <div className="bg-purple-50 rounded-xl p-4 border-2 border-purple-200">
                  <h4 className="font-bold text-lg text-purple-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Recommendations
                  </h4>
                  <p className="text-gray-700 whitespace-pre-line">{usageSummary.recommendations}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
