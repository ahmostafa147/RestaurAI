import { useState, useEffect } from 'react';
import { UtensilsCrossed, TrendingUp, TrendingDown, DollarSign, Sparkles, Award, RefreshCw, ChevronDown, ChevronUp, LineChart as LineChartIcon } from 'lucide-react';
import { api } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';

export function MenuDashboard() {
  const [menuData, setMenuData] = useState<any>(null);
  const [revenueAnalysis, setRevenueAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showRevenue, setShowRevenue] = useState(false);

  useEffect(() => {
    fetchMenuData();
  }, []);

  const fetchMenuData = async () => {
    try {
      setRefreshing(true);

      // Try to get Menu Agent analytics first
      const [data, revenue] = await Promise.all([
        api.getMenuAnalytics(),
        api.getRevenueAnalysis()
      ]);

      console.log('[Menu] Menu analytics:', data);
      console.log('[Menu] Revenue analysis:', revenue);

      // If Menu Agent data is null or empty, fallback to basic MCP menu data
      const hasAgentData = data && data.menu_items && data.menu_items.length > 0;
      if (!hasAgentData) {
        console.log('[Menu] No agent data available, falling back to MCP menu data');
        const mcpMenu = await api.getMenu();
        console.log('[Menu] MCP menu data:', mcpMenu);

        if (mcpMenu && mcpMenu.menu_items) {
          // Transform MCP menu data to match expected format
          const fallbackData = {
            summary_metrics: {
              total_menu_items: mcpMenu.menu_items.length,
              total_revenue: 0,
              total_orders: 0,
              average_order_value: 0
            },
            menu_items: mcpMenu.menu_items.map((item: any) => ({
              ...item,
              popularity: { order_count: 0, total_quantity: 0 },
              financial: { revenue: 0, order_count: 0, profit_margin_percentage: 0 }
            })),
            overall_insights: {
              llm_recommendations: {
                actionable_suggestions: ['Menu Agent not running. Start the Menu Agent to see detailed analytics and AI-powered insights.']
              }
            }
          };
          setMenuData(fallbackData);
          setRevenueAnalysis(revenue);
          setLoading(false);
          setRefreshing(false);
          return;
        }
      }

      setMenuData(data);
      setRevenueAnalysis(revenue);
    } catch (error) {
      console.error('Failed to fetch menu data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444'];

  // Extract data from the actual agent response
  const summaryMetrics = menuData?.summary_metrics || {};
  const menuItems = menuData?.menu_items || [];
  const overallInsights = menuData?.overall_insights || {};
  const llmRecommendations = overallInsights?.llm_recommendations || {};

  // Sort items by revenue for charts
  const topItemsByRevenue = [...menuItems]
    .sort((a: any, b: any) => (b.financial?.revenue || 0) - (a.financial?.revenue || 0))
    .slice(0, 8);

  const revenueData = topItemsByRevenue.map((item: any) => ({
    name: item.name.length > 15 ? item.name.substring(0, 15) + '...' : item.name,
    revenue: item.financial?.revenue || 0,
    orders: item.popularity?.order_count || 0,
    fullName: item.name
  }));

  // Group by category for pie chart
  const categoryMap = new Map<string, number>();
  menuItems.forEach((item: any) => {
    const category = item.category || 'Other';
    const revenue = item.financial?.revenue || 0;
    categoryMap.set(category, (categoryMap.get(category) || 0) + revenue);
  });

  const categoryData = Array.from(categoryMap.entries()).map(([name, value]) => ({
    name,
    value
  }));

  // Get low performers (items with low order count)
  const lowPerformers = [...menuItems]
    .filter((item: any) => (item.popularity?.order_count || 0) > 0)
    .sort((a: any, b: any) => (a.popularity?.order_count || 0) - (b.popularity?.order_count || 0))
    .slice(0, 4);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
          <p className="mt-4 text-gray-600">Loading menu analytics...</p>
        </div>
      </div>
    );
  }

  if (!menuData) {
    return (
      <div className="text-center py-12">
        <UtensilsCrossed className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 text-lg">No menu data available</p>
        <p className="text-gray-400 text-sm mt-2">Make sure the menu agent is running and has generated reports</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <DollarSign className="w-6 h-6" />
            </div>
            <button
              onClick={fetchMenuData}
              disabled={refreshing}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-2 rounded-lg transition-all"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="text-3xl font-bold mb-2">
            ${summaryMetrics.total_revenue?.toLocaleString() || '0'}
          </div>
          <div className="text-white/90">Total Revenue</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-amber-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <UtensilsCrossed className="w-6 h-6" />
            </div>
          </div>
          <div className="text-3xl font-bold mb-2">{summaryMetrics.total_orders || 0}</div>
          <div className="text-white/90">Total Orders</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>
          <div className="text-3xl font-bold mb-2">{summaryMetrics.total_menu_items || 0}</div>
          <div className="text-white/90">Menu Items</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>
          <div className="text-3xl font-bold mb-2">
            ${summaryMetrics.average_order_value?.toFixed(2) || '0.00'}
          </div>
          <div className="text-white/90">Avg Order Value</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue by Item */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-green-600" />
            Revenue by Top Items
          </h3>
          {revenueData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fill: '#666', fontSize: 11 }}
                />
                <YAxis tick={{ fill: '#666' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                  formatter={(value: any, name: string) => {
                    if (name === 'revenue') return [`$${value.toLocaleString()}`, 'Revenue'];
                    return [value, 'Orders'];
                  }}
                />
                <Bar dataKey="revenue" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No revenue data available
            </div>
          )}
        </div>

        {/* Revenue by Category */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <UtensilsCrossed className="w-6 h-6 text-orange-600" />
            Revenue by Category
          </h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: any) => [`$${value.toLocaleString()}`, 'Revenue']}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No category data available
            </div>
          )}
        </div>
      </div>

      {/* Top Performers */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Award className="w-6 h-6 text-yellow-600" />
          Top Performing Items
        </h3>

        {topItemsByRevenue.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topItemsByRevenue.slice(0, 6).map((item: any, index: number) => (
              <div
                key={item.item_id}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-orange-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                        index === 0 ? 'bg-yellow-500' :
                        index === 1 ? 'bg-gray-400' :
                        index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                      }`}>
                        {index + 1}
                      </div>
                      <h4 className="font-bold text-gray-900">{item.name}</h4>
                    </div>
                    {item.category && (
                      <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                        {item.category}
                      </span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-4">
                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="text-xs text-green-600 mb-1">Revenue</div>
                    <div className="text-lg font-bold text-green-700">
                      ${item.financial?.revenue?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-xs text-blue-600 mb-1">Orders</div>
                    <div className="text-lg font-bold text-blue-700">
                      {item.popularity?.order_count || 0}
                    </div>
                  </div>
                </div>

                {item.llm_insights?.estimated_prep_time_minutes && item.llm_insights.estimated_prep_time_minutes > 0 && (
                  <div className="mt-3 text-sm text-gray-600 flex items-center gap-2">
                    <span>Prep time: {item.llm_insights.estimated_prep_time_minutes}m</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            No menu items data available
          </div>
        )}
      </div>

      {/* AI Recommendations */}
      {llmRecommendations && llmRecommendations.actionable_suggestions && llmRecommendations.actionable_suggestions.length > 0 && (
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-600" />
            AI-Powered Menu Recommendations
          </h3>

          <div className="space-y-4">
            {llmRecommendations.actionable_suggestions.map((suggestion: string, index: number) => (
              <div key={index} className="bg-white rounded-xl p-5 border border-purple-200">
                <div className="flex items-start gap-4">
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-700">{suggestion}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Low Performers */}
      {lowPerformers.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingDown className="w-6 h-6 text-red-600" />
            Items Needing Attention
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {lowPerformers.map((item: any) => (
              <div
                key={item.item_id}
                className="border-2 border-red-200 bg-red-50 rounded-xl p-5"
              >
                <h4 className="font-bold text-lg text-gray-900 mb-3">{item.name}</h4>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-sm text-gray-600">Revenue</div>
                    <div className="text-xl font-bold text-gray-900">
                      ${item.financial?.revenue?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Orders</div>
                    <div className="text-xl font-bold text-gray-900">
                      {item.popularity?.order_count || 0}
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-red-200">
                  <div className="text-sm text-red-700 font-medium">
                    Consider reviewing this item's pricing, presentation, or menu placement
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revenue Analysis Section */}
      {revenueAnalysis && (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <button
            onClick={() => setShowRevenue(!showRevenue)}
            className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-3 rounded-xl text-white">
                <LineChartIcon className="w-6 h-6" />
              </div>
              <div className="text-left">
                <h3 className="text-xl font-bold text-gray-900">Revenue Analysis</h3>
                <p className="text-sm text-gray-600">Detailed revenue breakdown and trends</p>
              </div>
            </div>
            {showRevenue ? (
              <ChevronUp className="w-6 h-6 text-gray-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-gray-400" />
            )}
          </button>

          {showRevenue && (
            <div className="p-6 pt-0 space-y-6 border-t border-gray-100">
              {/* Revenue Summary Stats */}
              {revenueAnalysis.summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {revenueAnalysis.summary.total_revenue !== undefined && (
                    <div className="bg-green-50 rounded-xl p-4 border-2 border-green-200">
                      <div className="text-3xl font-bold text-green-600">
                        ${typeof revenueAnalysis.summary.total_revenue === 'number'
                          ? revenueAnalysis.summary.total_revenue.toLocaleString()
                          : revenueAnalysis.summary.total_revenue}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">Total Revenue</div>
                    </div>
                  )}
                  {revenueAnalysis.summary.average_revenue !== undefined && (
                    <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
                      <div className="text-3xl font-bold text-blue-600">
                        ${typeof revenueAnalysis.summary.average_revenue === 'number'
                          ? revenueAnalysis.summary.average_revenue.toFixed(2)
                          : revenueAnalysis.summary.average_revenue}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">Avg Revenue</div>
                    </div>
                  )}
                  {revenueAnalysis.summary.top_category !== undefined && (
                    <div className="bg-purple-50 rounded-xl p-4 border-2 border-purple-200">
                      <div className="text-2xl font-bold text-purple-600 truncate">
                        {revenueAnalysis.summary.top_category}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">Top Category</div>
                    </div>
                  )}
                  {revenueAnalysis.summary.growth_rate !== undefined && (
                    <div className="bg-orange-50 rounded-xl p-4 border-2 border-orange-200">
                      <div className="text-3xl font-bold text-orange-600">
                        {revenueAnalysis.summary.growth_rate}%
                      </div>
                      <div className="text-sm text-gray-600 mt-1">Growth Rate</div>
                    </div>
                  )}
                </div>
              )}

              {/* Revenue by Category or Time Period */}
              {revenueAnalysis.by_category && revenueAnalysis.by_category.length > 0 && (
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-4">Revenue by Category</h4>
                  <div className="space-y-3">
                    {revenueAnalysis.by_category.map((cat: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-4 bg-gray-50 rounded-xl p-4">
                        <div className="flex-grow">
                          <div className="font-semibold text-gray-900">{cat.category || cat.name}</div>
                          <div className="text-sm text-gray-600">
                            {cat.item_count || cat.count} items
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-600">
                            ${typeof cat.revenue === 'number' ? cat.revenue.toLocaleString() : cat.revenue}
                          </div>
                          {cat.percentage && (
                            <div className="text-sm text-gray-600">{cat.percentage}%</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Revenue Trends Chart */}
              {revenueAnalysis.trends && revenueAnalysis.trends.length > 0 && (
                <div>
                  <h4 className="font-bold text-lg text-gray-900 mb-4">Revenue Trends</h4>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={revenueAnalysis.trends}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis
                        dataKey="period"
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
                        formatter={(value: any) => [`$${value.toLocaleString()}`, 'Revenue']}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="revenue"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ fill: '#10b981', r: 5 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* AI Insights */}
              {revenueAnalysis.insights && (
                <div className="bg-green-50 rounded-xl p-4 border-2 border-green-200">
                  <h4 className="font-bold text-lg text-green-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Revenue Insights
                  </h4>
                  <p className="text-gray-700 whitespace-pre-line">{revenueAnalysis.insights}</p>
                </div>
              )}

              {/* Recommendations */}
              {revenueAnalysis.recommendations && (
                <div className="bg-blue-50 rounded-xl p-4 border-2 border-blue-200">
                  <h4 className="font-bold text-lg text-blue-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Recommendations
                  </h4>
                  <p className="text-gray-700 whitespace-pre-line">{revenueAnalysis.recommendations}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
