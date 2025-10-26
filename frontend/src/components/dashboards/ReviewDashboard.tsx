import { useState, useEffect } from 'react';
import { Star, TrendingUp, AlertCircle, Users, ThumbsUp, ThumbsDown, Sparkles, RefreshCw, MessageSquare } from 'lucide-react';
import { api } from '../../services/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

export function ReviewDashboard() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchReviewData();
  }, []);

  const fetchReviewData = async () => {
    try {
      setRefreshing(true);
      const data = await api.getReviewAnalytics();
      console.log('[Review] Review analytics:', data);
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch review analytics:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const COLORS = {
    positive: '#10b981',
    neutral: '#f59e0b',
    negative: '#ef4444',
    mixed: '#8b5cf6'
  };

  const sentimentData = analytics?.basic_metrics?.sentiment_breakdown
    ? Object.entries(analytics.basic_metrics.sentiment_breakdown).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value: value as number,
        color: COLORS[key as keyof typeof COLORS] || '#6366f1'
      }))
    : [];

  const ratingData = analytics?.basic_metrics?.rating_distribution
    ? Object.entries(analytics.basic_metrics.rating_distribution)
        .sort(([a], [b]) => Number(b) - Number(a))
        .map(([rating, count]) => ({
          rating: `${rating} ⭐`,
          count: count as number
        }))
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="mt-4 text-gray-600">Loading review analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 text-lg">No review data available</p>
      </div>
    );
  }

  const overallPerf = analytics.basic_metrics?.overall_performance || {};
  const topMentions = analytics.menu_analytics?.top_mentioned_items?.slice(0, 6) || [];
  const staffPerf = analytics.staff_analytics?.top_staff || [];

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Star className="w-6 h-6" />
            </div>
            <button
              onClick={fetchReviewData}
              disabled={refreshing}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-2 rounded-lg transition-all"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="text-4xl font-bold mb-2">
            {overallPerf.average_rating?.toFixed(1) || '0.0'}
          </div>
          <div className="text-white/90">Average Rating</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <MessageSquare className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">
            {analytics.metadata?.total_reviews || 0}
          </div>
          <div className="text-white/90">Total Reviews</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <ThumbsUp className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">
            {sentimentData.find(s => s.name === 'Positive')?.value || 0}
          </div>
          <div className="text-white/90">Positive Reviews</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">
            {analytics.metadata?.processed_reviews || 0}
          </div>
          <div className="text-white/90">AI Processed</div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <ThumbsUp className="w-6 h-6 text-green-600" />
            Sentiment Distribution
          </h3>
          {sentimentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No sentiment data available
            </div>
          )}
        </div>

        {/* Rating Distribution */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Star className="w-6 h-6 text-yellow-600" />
            Rating Distribution
          </h3>
          {ratingData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ratingData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fill: '#666' }} />
                <YAxis dataKey="rating" type="category" tick={{ fill: '#666' }} width={60} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '12px'
                  }}
                />
                <Bar dataKey="count" fill="#f59e0b" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-400">
              No rating data available
            </div>
          )}
        </div>
      </div>

      {/* Customer Insights */}
      {analytics.customer_insights && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-600" />
            Customer Insights
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Value Seekers */}
            {analytics.customer_insights.value_seekers && (
              <div className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-green-100 p-3 rounded-xl">
                    <ThumbsUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">Value Seekers</h4>
                    <div className="text-2xl font-bold text-green-600">
                      {analytics.customer_insights.value_seekers.count}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Common Themes:</strong>
                  <ul className="mt-2 space-y-1">
                    {analytics.customer_insights.value_seekers.common_themes?.slice(0, 3).map((theme: string, i: number) => (
                      <li key={i} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-green-600 rounded-full"></div>
                        {theme}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Experience Focused */}
            {analytics.customer_insights.experience_focused && (
              <div className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-purple-100 p-3 rounded-xl">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">Experience Focused</h4>
                    <div className="text-2xl font-bold text-purple-600">
                      {analytics.customer_insights.experience_focused.count}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Common Themes:</strong>
                  <ul className="mt-2 space-y-1">
                    {analytics.customer_insights.experience_focused.common_themes?.slice(0, 3).map((theme: string, i: number) => (
                      <li key={i} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-purple-600 rounded-full"></div>
                        {theme}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Critics */}
            {analytics.customer_insights.critics && (
              <div className="border-2 border-red-200 bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="bg-red-100 p-3 rounded-xl">
                    <ThumbsDown className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">Critics</h4>
                    <div className="text-2xl font-bold text-red-600">
                      {analytics.customer_insights.critics.count}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-gray-700">
                  <strong>Common Complaints:</strong>
                  <ul className="mt-2 space-y-1">
                    {analytics.customer_insights.critics.common_themes?.slice(0, 3).map((theme: string, i: number) => (
                      <li key={i} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-red-600 rounded-full"></div>
                        {theme}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Top Mentioned Menu Items */}
      {topMentions.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-orange-600" />
            Most Mentioned Menu Items
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topMentions.map((item: any, index: number) => (
              <div
                key={index}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-orange-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-bold text-lg text-gray-900">{item.item_name}</h4>
                  <div className="bg-orange-100 px-3 py-1 rounded-full">
                    <span className="text-orange-600 font-bold">{item.mention_count}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Positive</span>
                    <span className="font-semibold text-green-600">
                      {item.sentiment_breakdown?.positive || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Negative</span>
                    <span className="font-semibold text-red-600">
                      {item.sentiment_breakdown?.negative || 0}
                    </span>
                  </div>
                </div>

                {item.common_phrases && item.common_phrases.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="text-xs text-gray-600 mb-2">Common phrases:</div>
                    <div className="flex flex-wrap gap-1">
                      {item.common_phrases.slice(0, 3).map((phrase: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-700">
                          {phrase}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Staff Performance */}
      {staffPerf && staffPerf.length > 0 && (
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-600" />
            Staff Performance Highlights
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {staffPerf.map((staff: any, index: number) => (
              <div
                key={index}
                className="bg-white border-2 border-blue-200 rounded-xl p-5"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-bold text-lg text-gray-900">{staff.staff_name}</h4>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{staff.mention_count}</div>
                    <div className="text-xs text-gray-600">mentions</div>
                  </div>
                </div>

                <div className="space-y-2 mb-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Positive</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{
                            width: `${((staff.positive_mentions / staff.mention_count) * 100)}%`
                          }}
                        ></div>
                      </div>
                      <span className="font-semibold text-green-600 w-8">
                        {staff.positive_mentions}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Negative</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-red-500"
                          style={{
                            width: `${((staff.negative_mentions / staff.mention_count) * 100)}%`
                          }}
                        ></div>
                      </div>
                      <span className="font-semibold text-red-600 w-8">
                        {staff.negative_mentions}
                      </span>
                    </div>
                  </div>
                </div>

                {staff.common_contexts && staff.common_contexts.length > 0 && (
                  <div className="pt-3 border-t border-blue-200">
                    <div className="text-xs text-gray-600 mb-2">Mentioned for:</div>
                    <div className="flex flex-wrap gap-1">
                      {staff.common_contexts.slice(0, 3).map((context: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-blue-100 rounded-full text-blue-700">
                          {context}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reputation Alerts */}
      {analytics.reputation_insights?.anomaly_flags && (
        <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-2xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-red-600" />
            Reputation Alerts
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(analytics.reputation_insights.anomaly_flags).map(([key, value]: [string, any]) => {
              if (value > 0) {
                return (
                  <div key={key} className="bg-white border-2 border-red-200 rounded-xl p-5">
                    <div className="flex items-center gap-3">
                      <div className="bg-red-100 p-3 rounded-xl">
                        <AlertCircle className="w-6 h-6 text-red-600" />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900">
                          {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                        </h4>
                        <div className="text-2xl font-bold text-red-600">{value}</div>
                      </div>
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        </div>
      )}
    </div>
  );
}
