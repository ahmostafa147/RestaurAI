import { X, Star, TrendingUp, Users, AlertTriangle, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ReviewAnalytics {
  metadata: {
    total_reviews: number;
    processed_reviews: number;
  };
  basic_metrics: {
    overall_performance: {
      average_rating: number;
    };
    rating_breakdown: {
      rating_distribution: Record<string, number>;
    };
  };
  menu_analytics: {
    items: Array<{
      name: string;
      mention_count: number;
      sentiment_score: number;
    }>;
  };
  staff_analytics: {
    by_person: Array<{
      name: string;
      role: string;
      positive_count: number;
      negative_count: number;
      specific_feedback: string[];
    }>;
  };
  temporal_analysis: {
    trends: {
      trend_direction: string;
    };
  };
  reputation_insights: {
    sentiment_distribution: Record<string, number>;
    top_positive_phrases: Record<string, number>;
    top_negative_phrases: Record<string, number>;
  };
}

interface ReviewPanelProps {
  onClose: () => void;
}

export function ReviewPanel({ onClose }: ReviewPanelProps) {
  const [data, setData] = useState<ReviewAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/review-api/analytics')
      .then(res => res.json())
      .then(res => {
        const analytics = JSON.parse(res.response);
        setData(analytics);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const topMenu = data?.menu_analytics.items.slice(0, 5) || [];
  const topStaff = data?.staff_analytics.by_person.slice(0, 5) || [];
  const positives = Object.entries(data?.reputation_insights.top_positive_phrases || {}).slice(0, 3);
  const negatives = Object.entries(data?.reputation_insights.top_negative_phrases || {}).slice(0, 3);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-slideUp">
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-purple-50 to-pink-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Review Analytics</h2>
            <p className="text-sm text-gray-500 mt-1">
              {data?.metadata.total_reviews} total reviews • {data?.metadata.processed_reviews} analyzed
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-white rounded-lg">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-4 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="flex items-center justify-center gap-2 text-3xl font-bold text-yellow-600">
              {data?.basic_metrics.overall_performance.average_rating.toFixed(1) || 0}
              <Star className="w-6 h-6 fill-yellow-600" />
            </div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Avg Rating</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-blue-600">{data?.metadata.total_reviews || 0}</div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Total Reviews</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="flex items-center justify-center gap-2">
              <TrendingUp className={`w-6 h-6 ${data?.temporal_analysis.trends.trend_direction === 'improving' ? 'text-green-600' : 'text-red-600'}`} />
              <span className="text-lg font-bold text-gray-900 capitalize">{data?.temporal_analysis.trends.trend_direction || 'stable'}</span>
            </div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Trend</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-green-600">
              {data?.reputation_insights.sentiment_distribution.positive || 0}
            </div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Positive</div>
          </div>
        </div>

        <div className="overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading analytics...</div>
          ) : (
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Star className="w-5 h-5 text-yellow-600" />
                  <h3 className="font-semibold text-gray-900">Top Menu Items</h3>
                </div>
                <div className="space-y-2">
                  {topMenu.length > 0 ? topMenu.map((item, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <span className="font-medium text-gray-900">{item.name}</span>
                        <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">
                          {item.mention_count} mentions
                        </span>
                      </div>
                      <div className="mt-1 flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${item.sentiment_score > 0 ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-xs text-gray-600">
                          {item.sentiment_score > 0 ? 'Positive' : 'Negative'} sentiment
                        </span>
                      </div>
                    </div>
                  )) : <p className="text-sm text-gray-500">No menu mentions yet</p>}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Users className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">Staff Highlights</h3>
                </div>
                <div className="space-y-2">
                  {topStaff.length > 0 ? topStaff.map((staff, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="font-medium text-gray-900">{staff.name}</span>
                          <span className="text-xs text-gray-500 ml-2">({staff.role})</span>
                        </div>
                        <div className="flex gap-1">
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                            +{staff.positive_count}
                          </span>
                          {staff.negative_count > 0 && (
                            <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                              -{staff.negative_count}
                            </span>
                          )}
                        </div>
                      </div>
                      {staff.specific_feedback[0] && (
                        <p className="text-xs text-gray-600 mt-1 italic">"{staff.specific_feedback[0]}"</p>
                      )}
                    </div>
                  )) : <p className="text-sm text-gray-500">No staff mentions yet</p>}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <ThumbsUp className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-gray-900">Top Praise</h3>
                </div>
                <div className="space-y-2">
                  {positives.length > 0 ? positives.map(([phrase, count], idx) => (
                    <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-sm text-gray-900 italic">"{phrase}"</p>
                      <span className="text-xs text-green-700 mt-1 block">{count} mention{count > 1 ? 's' : ''}</span>
                    </div>
                  )) : <p className="text-sm text-gray-500">No positive phrases yet</p>}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <ThumbsDown className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold text-gray-900">Areas to Improve</h3>
                </div>
                <div className="space-y-2">
                  {negatives.length > 0 ? negatives.map(([phrase, count], idx) => (
                    <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-sm text-gray-900 italic">"{phrase}"</p>
                      <span className="text-xs text-red-700 mt-1 block">{count} mention{count > 1 ? 's' : ''}</span>
                    </div>
                  )) : (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                      <p className="text-sm text-green-700 font-medium">No negative feedback!</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t p-6 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-sm hover:shadow"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
