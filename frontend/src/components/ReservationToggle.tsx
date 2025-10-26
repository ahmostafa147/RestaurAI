import { useState } from 'react';
import { Calendar, Phone } from 'lucide-react';
import { AgentCard } from './AgentCard';

export function ReservationToggle() {
  const [enabled, setEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      const newState = !enabled;
      // TODO: Implement toggleReservations in API
      setEnabled(newState);
    } catch (error) {
      console.error('Failed to toggle reservations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AgentCard
      title="Reservation Agent"
      description="Bookings & table management"
      icon={Calendar}
      status={enabled ? 'active' : 'disabled'}
      metrics={[
        { label: 'Today', value: 12 },
        { label: 'Pending', value: 3 },
        { label: 'Tables', value: 18 },
      ]}
      action={
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-colors ${
            enabled
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <Phone className="w-4 h-4" />
          {enabled ? 'Accepting Reservations' : 'Reservations Disabled'}
        </button>
      }
    />
  );
}
