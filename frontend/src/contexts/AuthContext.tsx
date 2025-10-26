import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { accountStorage } from '../utils/localStorage';
import { callMCPTool } from '../utils/mcpClient';
import { api } from '../services/api';

interface Restaurant {
  name: string;
  secureKey: string;
}

interface AuthContextType {
  restaurant: Restaurant | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  signup: (username: string, password: string, restaurantName: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const savedRestaurant = localStorage.getItem('restaurant');
    if (savedRestaurant) {
      try {
        const restaurantData = JSON.parse(savedRestaurant);
        setRestaurant(restaurantData);
        // Set the secure key in the API service
        api.setSecureKey(restaurantData.secureKey);
      } catch (error) {
        console.error('Failed to parse saved restaurant:', error);
        localStorage.removeItem('restaurant');
      }
    }
    setIsLoading(false);
  }, []);

  const signup = async (username: string, password: string, restaurantName: string): Promise<{ success: boolean; error?: string }> => {
    try {
      setIsLoading(true);

      // Check if username already exists
      if (accountStorage.exists(username)) {
        setIsLoading(false);
        return { success: false, error: 'Username already exists' };
      }

      // Authenticate with backend to get secure key
      const result = await callMCPTool('authenticate_restaurant', {
        restaurant_name: restaurantName,
        password: ''
      });

      const parsedResult = typeof result === 'string' ? JSON.parse(result) : result;

      if (parsedResult.success) {
        // Create local account
        const created = accountStorage.create(username, password, restaurantName);
        if (!created) {
          setIsLoading(false);
          return { success: false, error: 'Failed to create account' };
        }

        // Auto-login after signup
        const restaurantData = {
          name: parsedResult.restaurant_name,
          secureKey: parsedResult.secure_key
        };
        setRestaurant(restaurantData);
        localStorage.setItem('restaurant', JSON.stringify(restaurantData));
        // Set the secure key in the API service
        api.setSecureKey(restaurantData.secureKey);
        setIsLoading(false);
        return { success: true };
      }

      setIsLoading(false);
      return { success: false, error: 'Invalid restaurant name' };
    } catch (error) {
      console.error('Signup failed:', error);
      setIsLoading(false);
      return { success: false, error: 'Signup failed. Please try again.' };
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      // Authenticate with local storage
      const restaurantName = accountStorage.authenticate(username, password);
      if (!restaurantName) {
        setIsLoading(false);
        return false;
      }

      // Get secure key from backend
      const result = await callMCPTool('authenticate_restaurant', {
        restaurant_name: restaurantName,
        password: ''
      });

      const parsedResult = typeof result === 'string' ? JSON.parse(result) : result;

      if (parsedResult.success) {
        const restaurantData = {
          name: parsedResult.restaurant_name,
          secureKey: parsedResult.secure_key
        };
        setRestaurant(restaurantData);
        localStorage.setItem('restaurant', JSON.stringify(restaurantData));
        // Set the secure key in the API service
        api.setSecureKey(restaurantData.secureKey);
        setIsLoading(false);
        return true;
      }

      setIsLoading(false);
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = () => {
    setRestaurant(null);
    localStorage.removeItem('restaurant');
    // Clear the secure key from API service
    api.setSecureKey('');
  };

  return (
    <AuthContext.Provider
      value={{
        restaurant,
        isAuthenticated: !!restaurant,
        login,
        signup,
        logout,
        isLoading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
