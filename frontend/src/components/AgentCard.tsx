import { LucideIcon } from 'lucide-react';
import type { AgentStatus } from '../types';

interface AgentCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  status: AgentStatus;
  metrics?: Array<{ label: string; value: string | number }>;
  action?: React.ReactNode;
}

const statusColors = {
  active: 'bg-green-100 text-green-800 border-green-200',
  idle: 'bg-gray-100 text-gray-800 border-gray-200',
  disabled: 'bg-red-100 text-red-800 border-red-200',
  pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
};

export function AgentCard({ title, description, icon: Icon, status, metrics, action }: AgentCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2.5 rounded-lg">
              <Icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-500">{description}</p>
            </div>
          </div>
          <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${statusColors[status]}`}>
            {status}
          </span>
        </div>

        {metrics && metrics.length > 0 && (
          <div className="grid grid-cols-3 gap-4 mb-4">
            {metrics.map((metric, idx) => (
              <div key={idx} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                <div className="text-xs text-gray-500">{metric.label}</div>
              </div>
            ))}
          </div>
        )}

        {action && <div className="mt-4 pt-4 border-t border-gray-100">{action}</div>}
      </div>
    </div>
  );
}
