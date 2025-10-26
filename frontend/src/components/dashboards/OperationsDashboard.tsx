import { useState, useEffect } from 'react';
import { Calendar, ShoppingBag, Users, CheckCircle, XCircle, RefreshCw, Plus, Utensils } from 'lucide-react';
import { api, MenuItem } from '../../services/api';

interface Reservation {
  id: number;
  name: string;
  party_size: number;
  time: string;
  table_number?: number;
  status: string;
}

interface Order {
  id: number;
  table_number: number;
  items: Array<{ item_id: number; quantity: number; name?: string }>;
  total: number;
  status: string;
  timestamp: string;
}

export function OperationsDashboard() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Form states
  const [showReservationForm, setShowReservationForm] = useState(false);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [reservationName, setReservationName] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [reservationTime, setReservationTime] = useState('');
  const [orderTableNumber, setOrderTableNumber] = useState(1);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  useEffect(() => {
    fetchOperationsData();
  }, []);

  const fetchOperationsData = async () => {
    try {
      setRefreshing(true);
      const [resData, ordersData, menuData] = await Promise.all([
        api.getReservations(),
        api.getOrders(),
        api.getMenu()
      ]);

      console.log('[Operations] Reservations:', resData);
      console.log('[Operations] Orders:', ordersData);
      console.log('[Operations] Menu:', menuData);

      setReservations(resData.reservations || []);
      setOrders(ordersData.orders || []);
      setMenuItems(menuData.menu_items || []);
    } catch (error) {
      console.error('Failed to fetch operations data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleCreateReservation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.reserveTable(reservationName, partySize, reservationTime);
      setShowReservationForm(false);
      setReservationName('');
      setPartySize(2);
      setReservationTime('');
      fetchOperationsData();
    } catch (error) {
      console.error('Failed to create reservation:', error);
    }
  };

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.placeOrder(orderTableNumber, selectedItems);
      setShowOrderForm(false);
      setOrderTableNumber(1);
      setSelectedItems([]);
      fetchOperationsData();
    } catch (error) {
      console.error('Failed to place order:', error);
    }
  };

  const handleSeatParty = async (tableNumber: number) => {
    try {
      await api.seatParty(tableNumber);
      fetchOperationsData();
    } catch (error) {
      console.error('Failed to seat party:', error);
    }
  };

  const handleClearTable = async (tableNumber: number) => {
    try {
      await api.clearTable(tableNumber);
      fetchOperationsData();
    } catch (error) {
      console.error('Failed to clear table:', error);
    }
  };

  const toggleItemSelection = (itemId: number) => {
    setSelectedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading operations data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Calendar className="w-6 h-6" />
            </div>
            <button
              onClick={fetchOperationsData}
              disabled={refreshing}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-2 rounded-lg transition-all"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="text-4xl font-bold mb-2">{reservations.length}</div>
          <div className="text-white/90">Active Reservations</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-amber-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <ShoppingBag className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">{orders.length}</div>
          <div className="text-white/90">Current Orders</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Utensils className="w-6 h-6" />
            </div>
          </div>
          <div className="text-4xl font-bold mb-2">{menuItems.length}</div>
          <div className="text-white/90">Menu Items</div>
        </div>
      </div>

      {/* Reservations Section */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-blue-600" />
            Reservations
          </h3>
          <button
            onClick={() => setShowReservationForm(!showReservationForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Reservation
          </button>
        </div>

        {showReservationForm && (
          <form onSubmit={handleCreateReservation} className="mb-6 p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Guest Name</label>
                <input
                  type="text"
                  value={reservationName}
                  onChange={(e) => setReservationName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="John Doe"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Party Size</label>
                <input
                  type="number"
                  value={partySize}
                  onChange={(e) => setPartySize(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                  max="20"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Time</label>
                <input
                  type="time"
                  value={reservationTime}
                  onChange={(e) => setReservationTime(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
              >
                Create Reservation
              </button>
              <button
                type="button"
                onClick={() => setShowReservationForm(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {reservations.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No active reservations</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reservations.map((reservation) => (
              <div
                key={reservation.id}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-lg text-gray-900">{reservation.name}</h4>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {reservation.party_size} guests
                      </span>
                      <span>{reservation.time}</span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    reservation.status === 'seated' ? 'bg-green-100 text-green-700' :
                    reservation.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {reservation.status}
                  </span>
                </div>

                {reservation.table_number && (
                  <div className="mb-3 text-sm text-gray-600">
                    Table: <span className="font-semibold">#{reservation.table_number}</span>
                  </div>
                )}

                {reservation.status === 'pending' && reservation.table_number && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSeatParty(reservation.table_number!)}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Seat Party
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Orders Section */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <ShoppingBag className="w-6 h-6 text-orange-600" />
            Orders
          </h3>
          <button
            onClick={() => setShowOrderForm(!showOrderForm)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Place Order
          </button>
        </div>

        {showOrderForm && (
          <div className="mb-6 p-4 bg-orange-50 rounded-xl border-2 border-orange-200">
            <form onSubmit={handlePlaceOrder}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Table Number</label>
                <input
                  type="number"
                  value={orderTableNumber}
                  onChange={(e) => setOrderTableNumber(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  min="1"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Select Items</label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-64 overflow-y-auto p-2 bg-white rounded-lg border border-gray-300">
                  {menuItems.map((item) => (
                    <button
                      key={item.item_id}
                      type="button"
                      onClick={() => toggleItemSelection(item.item_id)}
                      className={`p-3 rounded-lg border-2 transition-all text-left ${
                        selectedItems.includes(item.item_id)
                          ? 'border-orange-500 bg-orange-50'
                          : 'border-gray-200 hover:border-orange-300'
                      }`}
                    >
                      <div className="font-semibold text-sm text-gray-900">{item.name}</div>
                      <div className="text-xs text-gray-600">${item.price}</div>
                      {item.category && (
                        <div className="text-xs text-gray-500 mt-1">{item.category}</div>
                      )}
                    </button>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Selected: {selectedItems.length} items
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={selectedItems.length === 0}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Place Order
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowOrderForm(false);
                    setSelectedItems([]);
                  }}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-700 px-6 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {orders.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No current orders</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div
                key={order.id}
                className="border-2 border-gray-200 rounded-xl p-5 hover:border-orange-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-lg text-gray-900">Table #{order.table_number}</h4>
                    <div className="text-sm text-gray-600 mt-1">
                      {new Date(order.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">${order.total.toFixed(2)}</div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      order.status === 'completed' ? 'bg-green-100 text-green-700' :
                      order.status === 'preparing' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 mt-3">
                  <div className="text-sm font-semibold text-gray-700 mb-2">Items:</div>
                  <div className="space-y-1">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="text-sm text-gray-600 flex justify-between">
                        <span>{item.name || `Item #${item.item_id}`} × {item.quantity}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {order.status === 'completed' && (
                  <button
                    onClick={() => handleClearTable(order.table_number)}
                    className="mt-3 w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
                  >
                    <XCircle className="w-4 h-4" />
                    Clear Table
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
