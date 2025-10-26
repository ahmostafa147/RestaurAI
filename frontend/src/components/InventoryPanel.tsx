import { X, AlertTriangle, XCircle, Package } from 'lucide-react';
import { useEffect, useState } from 'react';

interface InventoryItem {
  name: string;
  quantity: number;
  unit: string;
}

interface InventoryData {
  lowStock: InventoryItem[];
  unavailable: InventoryItem[];
  totalItems: number;
  activeItems: number;
}

interface InventoryPanelProps {
  onClose: () => void;
}

export function InventoryPanel({ onClose }: InventoryPanelProps) {
  const [data, setData] = useState<InventoryData>({ lowStock: [], unavailable: [], totalItems: 0, activeItems: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/ingredient-api/metrics')
      .then(res => res.json())
      .then(res => {
        const metrics = JSON.parse(res.response);
        setData(metrics);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const critical = data.lowStock.filter(i => i.quantity < 0.5);
  const warning = data.lowStock.filter(i => i.quantity >= 0.5);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-fadeIn">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col animate-slideUp">
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Inventory Status</h2>
            <p className="text-sm text-gray-500 mt-1">{data.activeItems} active items • {data.totalItems} total</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-white rounded-lg">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-red-600">{critical.length}</div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Critical</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-yellow-600">{warning.length}</div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Low Stock</div>
          </div>
          <div className="bg-white rounded-lg p-4 text-center shadow-sm">
            <div className="text-3xl font-bold text-gray-600">{data.unavailable.length}</div>
            <div className="text-xs text-gray-600 mt-1 uppercase tracking-wide">Unavailable</div>
          </div>
        </div>

        <div className="overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">Loading inventory data...</div>
          ) : (
            <>
              {critical.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                    <h3 className="font-semibold text-gray-900">Critical Stock ({critical.length})</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {critical.map((item, idx) => (
                      <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <span className="font-medium text-gray-900">{item.name}</span>
                          <span className="text-red-700 font-semibold">{item.quantity} {item.unit}</span>
                        </div>
                        <div className="mt-2 text-xs text-red-600 font-medium">Immediate reorder required</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {warning.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Package className="w-5 h-5 text-yellow-600" />
                    <h3 className="font-semibold text-gray-900">Low Stock ({warning.length})</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {warning.map((item, idx) => (
                      <div key={idx} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <span className="font-medium text-gray-900">{item.name}</span>
                          <span className="text-yellow-700 font-semibold">{item.quantity} {item.unit}</span>
                        </div>
                        <div className="mt-2 text-xs text-yellow-600">Reorder soon</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {data.unavailable.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <XCircle className="w-5 h-5 text-gray-600" />
                    <h3 className="font-semibold text-gray-900">Unavailable Items ({data.unavailable.length})</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {data.unavailable.map((item, idx) => (
                      <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <span className="font-medium text-gray-900 line-through">{item.name}</span>
                          <span className="text-gray-500">{item.quantity} {item.unit}</span>
                        </div>
                        <div className="mt-2 text-xs text-gray-600">Expired or spoiled - remove from inventory</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {data.lowStock.length === 0 && data.unavailable.length === 0 && (
                <div className="text-center py-12">
                  <Package className="w-12 h-12 text-green-500 mx-auto mb-3" />
                  <p className="text-lg font-medium text-gray-900">All inventory levels healthy</p>
                  <p className="text-sm text-gray-500 mt-1">No low stock or unavailable items</p>
                </div>
              )}
            </>
          )}
        </div>

        <div className="border-t p-6 bg-gray-50 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-sm hover:shadow"
          >
            Close
          </button>
          <button
            onClick={() => {
              const csv = [
                ['Category', 'Name', 'Quantity', 'Unit'],
                ...critical.map(i => ['Critical', i.name, i.quantity, i.unit]),
                ...warning.map(i => ['Low Stock', i.name, i.quantity, i.unit]),
                ...data.unavailable.map(i => ['Unavailable', i.name, i.quantity, i.unit])
              ].map(row => row.join(',')).join('\n');
              const blob = new Blob([csv], { type: 'text/csv' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `inventory-${new Date().toISOString().split('T')[0]}.csv`;
              a.click();
            }}
            className="px-6 py-3 bg-white border-2 border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition-all"
          >
            Export CSV
          </button>
        </div>
      </div>
    </div>
  );
}
