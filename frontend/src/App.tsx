import { useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SignIn } from './components/SignIn';
import { MainDashboard } from './components/MainDashboard';
import { api } from './services/api';

function AppContent() {
  const { isAuthenticated, restaurant, isLoading } = useAuth();

  useEffect(() => {
    if (restaurant) {
      api.setSecureKey(restaurant.secureKey);
    }
  }, [restaurant]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <MainDashboard /> : <SignIn />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
