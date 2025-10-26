import { useState, useEffect } from 'react';
import { ChefHat, Loader2, Sparkles, TrendingUp, Shield, UserPlus, LogIn, Info } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { accountStorage } from '../utils/localStorage';
import { callMCPTool } from '../utils/mcpClient';

type AuthMode = 'signin' | 'signup';

export function SignIn() {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState<AuthMode>('signin');
  const [restaurants, setRestaurants] = useState<Array<{ name: string; id: string }>>([]);
  const [showTestCredentials, setShowTestCredentials] = useState(false);

  // Sign in form
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  // Sign up form
  const [signupUsername, setSignupUsername] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [loadingRestaurants, setLoadingRestaurants] = useState(true);

  useEffect(() => {
    // Initialize test accounts
    accountStorage.initialize();
    fetchRestaurants();
  }, []);

  const fetchRestaurants = async () => {
    try {
      const result = await callMCPTool('get_restaurants', {});
      const parsedResult = typeof result === 'string' ? JSON.parse(result) : result;
      setRestaurants(parsedResult.restaurants || []);
    } catch (error) {
      console.error('Failed to fetch restaurants:', error);
      // Set error only in signup mode
      if (mode === 'signup') {
        setError('Cannot connect to MCP server. Make sure it is running: python backend/src/mcp/http_server.py');
      }
    } finally {
      setLoadingRestaurants(false);
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please enter username and password');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const success = await login(username, password);
      if (!success) {
        setError('Invalid username or password. Click "Test Credentials Available" above to see valid test accounts.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to the server. Make sure the MCP server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!signupUsername || !signupPassword || !selectedRestaurant) {
      setError('Please fill in all fields');
      return;
    }

    if (signupPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (signupPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await signup(signupUsername, signupPassword, selectedRestaurant);
      if (!result.success) {
        setError(result.error || 'Signup failed. Please try again.');
      }
      // If successful, auth context will handle redirect
    } catch (err) {
      console.error('Signup error:', err);
      setError('Failed to connect to the server. Make sure the MCP server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl animate-pulse delay-700"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-2xl shadow-2xl mb-6 transform hover:scale-110 transition-transform duration-300">
            <ChefHat className="w-12 h-12 text-indigo-600" />
          </div>
          <h1 className="text-5xl font-bold text-white mb-3 tracking-tight">
            RestaurAI
          </h1>
          <p className="text-xl text-white/90 flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5" />
            AI-Powered Restaurant Management
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 transform hover:scale-[1.02] transition-all duration-300">
          {/* Tab Switcher */}
          <div className="flex gap-2 mb-6 p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => {
                setMode('signin');
                setError('');
              }}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
                mode === 'signin'
                  ? 'bg-white shadow-md text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <LogIn className="w-4 h-4" />
              Sign In
            </button>
            <button
              onClick={() => {
                setMode('signup');
                setError('');
              }}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
                mode === 'signup'
                  ? 'bg-white shadow-md text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <UserPlus className="w-4 h-4" />
              Sign Up
            </button>
          </div>

          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {mode === 'signin' ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-gray-600">
              {mode === 'signin'
                ? 'Sign in to access your restaurant dashboard'
                : 'Sign up to get started with RestaurAI'}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm animate-shake">
              {error}
            </div>
          )}

          {/* Test Credentials Section - Only show in sign-in mode */}
          {mode === 'signin' && (
            <div className="mb-6">
              <button
                type="button"
                onClick={() => setShowTestCredentials(!showTestCredentials)}
                className="w-full flex items-center justify-between p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl text-blue-700 text-sm font-medium transition-colors duration-200"
              >
                <div className="flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  <span>Test Credentials Available</span>
                </div>
                <span className="text-xs">{showTestCredentials ? '▼' : '▶'}</span>
              </button>

              {showTestCredentials && (
                <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-xl text-sm space-y-3">
                  <p className="font-semibold text-blue-900">Use these accounts to test:</p>
                  <div className="space-y-2 font-mono text-xs">
                    <div className="p-2 bg-white rounded border border-blue-100 flex items-start justify-between">
                      <div>
                        <div className="text-blue-700"><strong>Username:</strong> admin</div>
                        <div className="text-blue-700"><strong>Password:</strong> admin123</div>
                        <div className="text-gray-600 text-xs mt-1">Restaurant: Causwells</div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setUsername('admin');
                          setPassword('admin123');
                        }}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                      >
                        Use
                      </button>
                    </div>
                    <div className="p-2 bg-white rounded border border-blue-100 flex items-start justify-between">
                      <div>
                        <div className="text-blue-700"><strong>Username:</strong> manager</div>
                        <div className="text-blue-700"><strong>Password:</strong> manager123</div>
                        <div className="text-gray-600 text-xs mt-1">Restaurant: Cote Ouest Bistro</div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setUsername('manager');
                          setPassword('manager123');
                        }}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                      >
                        Use
                      </button>
                    </div>
                    <div className="p-2 bg-white rounded border border-blue-100 flex items-start justify-between">
                      <div>
                        <div className="text-blue-700"><strong>Username:</strong> test</div>
                        <div className="text-blue-700"><strong>Password:</strong> test123</div>
                        <div className="text-gray-600 text-xs mt-1">Restaurant: Causwells</div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setUsername('test');
                          setPassword('test123');
                        }}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
                      >
                        Use
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">
                    Make sure the MCP server is running: <code className="bg-white px-1 py-0.5 rounded">python backend/src/mcp/http_server.py</code>
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Sign In Form */}
          {mode === 'signin' && (
            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200"
                  placeholder="Enter your username"
                  disabled={isLoading}
                  required
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200"
                  placeholder="Enter your password"
                  disabled={isLoading}
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    <span>Sign In</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Sign Up Form */}
          {mode === 'signup' && (
            <form onSubmit={handleSignUp} className="space-y-4">
              <div>
                <label htmlFor="signup-username" className="block text-sm font-semibold text-gray-700 mb-2">
                  Username
                </label>
                <input
                  id="signup-username"
                  type="text"
                  value={signupUsername}
                  onChange={(e) => setSignupUsername(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200"
                  placeholder="Choose a username"
                  disabled={isLoading}
                  required
                />
              </div>

              <div>
                <label htmlFor="signup-password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <input
                  id="signup-password"
                  type="password"
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200"
                  placeholder="Create a password (min 6 characters)"
                  disabled={isLoading}
                  required
                />
              </div>

              <div>
                <label htmlFor="confirm-password" className="block text-sm font-semibold text-gray-700 mb-2">
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200"
                  placeholder="Confirm your password"
                  disabled={isLoading}
                  required
                />
              </div>

              <div>
                <label htmlFor="restaurant" className="block text-sm font-semibold text-gray-700 mb-2">
                  Select Your Restaurant
                </label>
                {loadingRestaurants ? (
                  <div className="flex items-center justify-center p-8 text-gray-400">
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span className="ml-2">Loading restaurants...</span>
                  </div>
                ) : restaurants.length === 0 ? (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-sm">
                    <p className="text-yellow-800 font-semibold mb-2">No restaurants available</p>
                    <p className="text-yellow-700 text-xs mb-2">
                      Make sure the MCP server is running to load available restaurants.
                    </p>
                    <code className="block bg-yellow-100 p-2 rounded text-xs text-yellow-900 mt-2">
                      python backend/src/mcp/http_server.py
                    </code>
                    <button
                      type="button"
                      onClick={() => {
                        setLoadingRestaurants(true);
                        fetchRestaurants();
                      }}
                      className="mt-3 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-xs font-semibold rounded-lg transition-colors duration-200"
                    >
                      Retry Loading Restaurants
                    </button>
                  </div>
                ) : (
                  <select
                    id="restaurant"
                    value={selectedRestaurant}
                    onChange={(e) => setSelectedRestaurant(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white text-gray-900 font-medium transition-all duration-200 cursor-pointer hover:border-indigo-300"
                    disabled={isLoading}
                    required
                  >
                    <option value="">Choose a restaurant...</option>
                    {restaurants.map((restaurant) => (
                      <option key={restaurant.id} value={restaurant.name}>
                        {restaurant.name}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading || loadingRestaurants}
                className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    <span>Create Account</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Features */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl">
                <TrendingUp className="w-6 h-6 text-indigo-600 mx-auto mb-2" />
                <p className="text-xs font-semibold text-gray-700">Real-time Analytics</p>
              </div>
              <div className="p-3 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
                <Sparkles className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                <p className="text-xs font-semibold text-gray-700">AI Insights</p>
              </div>
              <div className="p-3 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl">
                <Shield className="w-6 h-6 text-pink-600 mx-auto mb-2" />
                <p className="text-xs font-semibold text-gray-700">Secure Access</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-white/80 text-sm">
          <p>© 2024 RestaurAI. Powered by Claude AI.</p>
          <p className="mt-2 text-xs">
            {mode === 'signup'
              ? 'Test accounts are stored locally for development'
              : 'Available restaurants: Causwells, Cote Ouest Bistro'}
          </p>
        </div>
      </div>
    </div>
  );
}
