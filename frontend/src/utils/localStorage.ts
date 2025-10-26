// Local storage for managing test accounts
interface UserAccount {
  username: string;
  password: string;
  restaurantName: string;
  createdAt: string;
}

const ACCOUNTS_KEY = 'restaurai_accounts';

// Default test accounts
const DEFAULT_ACCOUNTS: UserAccount[] = [
  {
    username: 'admin',
    password: 'admin123',
    restaurantName: 'Causwells',
    createdAt: new Date().toISOString()
  },
  {
    username: 'manager',
    password: 'manager123',
    restaurantName: 'Cote Ouest Bistro',
    createdAt: new Date().toISOString()
  },
  {
    username: 'test',
    password: 'test123',
    restaurantName: 'Causwells',
    createdAt: new Date().toISOString()
  }
];

export const accountStorage = {
  // Initialize default accounts if needed
  initialize(): void {
    const data = localStorage.getItem(ACCOUNTS_KEY);
    if (!data) {
      localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(DEFAULT_ACCOUNTS));
    }
  },

  // Get all accounts
  getAll(): UserAccount[] {
    this.initialize();
    const data = localStorage.getItem(ACCOUNTS_KEY);
    return data ? JSON.parse(data) : DEFAULT_ACCOUNTS;
  },

  // Create new account
  create(username: string, password: string, restaurantName: string): boolean {
    const accounts = this.getAll();

    // Check if username already exists
    if (accounts.some(acc => acc.username === username)) {
      return false;
    }

    accounts.push({
      username,
      password, // In production, this would be hashed!
      restaurantName,
      createdAt: new Date().toISOString()
    });

    localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));
    return true;
  },

  // Authenticate user
  authenticate(username: string, password: string): string | null {
    const accounts = this.getAll();
    const account = accounts.find(acc =>
      acc.username === username && acc.password === password
    );
    return account ? account.restaurantName : null;
  },

  // Check if username exists
  exists(username: string): boolean {
    return this.getAll().some(acc => acc.username === username);
  }
};
