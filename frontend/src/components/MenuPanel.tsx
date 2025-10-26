import { X, TrendingUp, TrendingDown, DollarSign, ShoppingCart } from 'lucide-react';
import { useEffect, useState } from 'react';

interface MenuItem {
  name: string;
  orders: number;
  revenue: number;
}

interface MenuData {
  totalItems: number;
  activeItems: number;
  topPerformers: MenuItem[];
  lowPerformers: MenuItem[];
}

interface MenuPanelProps {
  onClose: () => void;
}

export function MenuPanel({ onClose }: MenuPanelProps) {
  const [data, setData] = useState<MenuData>({ totalItems: 0, activeItems: 0, topPerformers: [], lowPerformers: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/menu-api/metrics')
      .then(res => res.json())
      .then(res => {
        const metrics = JSON.parse(res.response);
        setData(metrics);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const totalRevenue = [...data.topPerformers, ...data.lowPerformers].reduce((sum, item) => sum + item.revenue, 0);
  const totalOrders = [...data.topPerformers, ...data.lowPerformers].reduce((sum, item) => sum + item.orders, 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-slideUp">
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-orange-50 to-amber-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Menu Performance</h2>
            <p className="text-sm text-gray-500 mt-1">{data.activeItems} active items • {data.totalItems} total</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-white rounded-lg">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="flex items-center justify-center gap-2 text-3xl font-bold text-blue-600">
              <ShoppingCart className="w-7 h-7" />
              {totalOrders}
            </div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Total Orders</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="flex items-center justify-center gap-2 text-3xl font-bold text-green-600">
              <DollarSign className="w-7 h-7" />
              {totalRevenue.toFixed(0)}
            </div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Revenue</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-orange-600">{data.activeItems}</div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Active Items</div>
          </div>
        </div>

        <div className="overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading menu analytics...</div>
          ) : (
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-gray-900">Top Performers</h3>
                </div>
                <div className="space-y-3">
                  {data.topPerformers.map((item, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-gray-900">{item.name}</span>
                        <div className="flex items-center gap-1 bg-green-600 text-white text-xs px-2 py-1 rounded">
                          <TrendingUp className="w-3 h-3" />
                          #{idx + 1}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-600">Orders:</span>
                          <span className="font-semibold text-gray-900 ml-1">{item.orders}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Revenue:</span>
                          <span className="font-semibold text-green-700 ml-1">${item.revenue.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  {data.topPerformers.length === 0 && (
                    <p className="text-sm text-gray-500">No performance data available</p>
                  )}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold text-gray-900">Needs Attention</h3>
                </div>
                <div className="space-y-3">
                  {data.lowPerformers.map((item, idx) => (
                    <div key={idx} className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-gray-900">{item.name}</span>
                        <div className="flex items-center gap-1 bg-red-600 text-white text-xs px-2 py-1 rounded">
                          <TrendingDown className="w-3 h-3" />
                          Low
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-600">Orders:</span>
                          <span className="font-semibold text-gray-900 ml-1">{item.orders}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Revenue:</span>
                          <span className="font-semibold text-red-700 ml-1">${item.revenue.toFixed(2)}</span>
                        </div>
                      </div>
                      <p className="text-xs text-red-600 mt-2">Consider promotion or menu optimization</p>
                    </div>
                  ))}
                  {data.lowPerformers.length === 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <p className="text-sm text-green-700 font-medium">All items performing well!</p>
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
            className="w-full px-6 py-3 bg-gradient-to-r from-orange-600 to-amber-600 text-white font-medium rounded-lg hover:from-orange-700 hover:to-amber-700 transition-all shadow-sm hover:shadow"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
