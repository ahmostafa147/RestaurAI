import { useState } from 'react';
import {
  LayoutDashboard,
  Package,
  UtensilsCrossed,
  Star,
  LogOut,
  ChefHat,
  Menu as MenuIcon,
  X,
  Briefcase
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { OverviewDashboard } from './dashboards/OverviewDashboard';
import { InventoryDashboard } from './dashboards/InventoryDashboard';
import { MenuDashboard } from './dashboards/MenuDashboard';
import { ReviewDashboard } from './dashboards/ReviewDashboard';
import { OperationsDashboard } from './dashboards/OperationsDashboard';

type View = 'overview' | 'inventory' | 'menu' | 'reviews' | 'operations';

export function MainDashboard() {
  const { restaurant, logout } = useAuth();
  const [currentView, setCurrentView] = useState<View>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { id: 'overview', name: 'Overview', icon: LayoutDashboard, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { id: 'inventory', name: 'Inventory', icon: Package, color: 'text-blue-600', bg: 'bg-blue-50' },
    { id: 'menu', name: 'Menu Analytics', icon: UtensilsCrossed, color: 'text-orange-600', bg: 'bg-orange-50' },
    { id: 'reviews', name: 'Reviews', icon: Star, color: 'text-purple-600', bg: 'bg-purple-50' },
    { id: 'operations', name: 'Operations', icon: Briefcase, color: 'text-green-600', bg: 'bg-green-50' },
  ];

  const renderView = () => {
    switch (currentView) {
      case 'overview':
        return <OverviewDashboard />;
      case 'inventory':
        return <InventoryDashboard />;
      case 'menu':
        return <MenuDashboard />;
      case 'reviews':
        return <ReviewDashboard />;
      case 'operations':
        return <OperationsDashboard />;
      default:
        return <OverviewDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <ChefHat className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">RestaurAI</h1>
                <p className="text-xs text-gray-500">Powered by AI</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Restaurant Info */}
          <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Currently Managing</div>
            <div className="font-bold text-gray-900 truncate">{restaurant?.name}</div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setCurrentView(item.id as View);
                    setSidebarOpen(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                    ${isActive
                      ? `${item.bg} ${item.color} shadow-sm`
                      : 'text-gray-600 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl font-medium transition-all duration-200"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <header className="bg-white shadow-sm sticky top-0 z-30">
          <div className="px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden text-gray-600 hover:text-gray-900"
                >
                  <MenuIcon className="w-6 h-6" />
                </button>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {navigation.find(n => n.id === currentView)?.name}
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Real-time insights powered by AI
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-green-50 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-700">All Systems Active</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
