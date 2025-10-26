import { Package, Star, Users, UtensilsCrossed, ClipboardList } from 'lucide-react';
import { AgentCard } from './AgentCard';
import { ReservationToggle } from './ReservationToggle';

export function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Agent Overview</h2>
        <p className="text-sm text-gray-500">Manage your restaurant operations from one place</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ReservationToggle />

        <AgentCard
          title="Inventory Agent"
          description="Stock tracking & auto-ordering"
          icon={Package}
          status="active"
          metrics={[
            { label: 'Low Stock', value: 5 },
            { label: 'Total Items', value: 47 },
            { label: 'Orders', value: 2 },
          ]}
          action={
            <button className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              View Inventory
            </button>
          }
        />

        <AgentCard
          title="Review Agent"
          description="Monitor & respond to reviews"
          icon={Star}
          status="active"
          metrics={[
            { label: 'Unread', value: 8 },
            { label: 'Avg Rating', value: 4.3 },
            { label: 'Flagged', value: 2 },
          ]}
          action={
            <button className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              Review Dashboard
            </button>
          }
        />

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

      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="bg-blue-100 p-2 rounded-lg">
            <ClipboardList className="w-5 h-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">Agent Integration Pending</h3>
            <p className="text-sm text-gray-600">
              Connect backend agents to enable real-time data and autonomous operations.
              Each agent module is ready for integration once the corresponding backend service is implemented.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
