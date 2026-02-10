/**
 * Authentication Store
 * Manages authentication state including login, logout, and user data
 */

import { apiClient } from '../api/apiClient';

class AuthStore {
    constructor() {
        this.user = null;
        this.token = null;
        this.loading = false;
        this.listeners = [];
    }

    /**
     * Initialize auth state from localStorage
     */
    init() {
        if (typeof window === 'undefined') return;

        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('user');

        if (token && userStr) {
            try {
                this.token = token;
                this.user = JSON.parse(userStr);
                this.notifyListeners();
            } catch (error) {
                console.error('Failed to parse user data:', error);
                this.clearAuth();
            }
        }
    }

    /**
     * Subscribe to auth state changes
     */
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    /**
     * Notify all listeners of state change
     */
    notifyListeners() {
        this.listeners.forEach(listener => listener({
            user: this.user,
            token: this.token,
            loading: this.loading,
            isAuthenticated: this.isAuthenticated()
        }));
    }

    /**
     * Login with email and password
     */
    async login(email, password) {
        try {
            this.loading = true;
            this.notifyListeners();

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            console.log('Login response:', data); // Debug log

            // Backend returns 'token', not 'access_token'
            this.token = data.token;
            this.user = data.user;

            if (typeof window !== 'undefined') {
                localStorage.setItem('access_token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
            }

            this.loading = false;
            this.notifyListeners();

            return data;
        } catch (error) {
            this.loading = false;
            this.notifyListeners();
            throw error;
        }
    }

    /**
     * Quick demo login (for demo account)
     */
    async demoLogin() {
        return this.login('admin@hpcl.com', 'admin123');
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            // Call backend logout endpoint
            await apiClient.post('/api/auth/logout');
        } catch (error) {
            console.error('Logout API call failed:', error);
        } finally {
            this.clearAuth();
        }
    }

    /**
     * Clear authentication data
     */
    clearAuth() {
        this.user = null;
        this.token = null;

        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
        }

        this.notifyListeners();
    }

    /**
     * Get current user
     */
    async getCurrentUser() {
        try {
            const user = await apiClient.get('/api/auth/me');
            this.user = user;

            if (typeof window !== 'undefined') {
                localStorage.setItem('user', JSON.stringify(user));
            }

            this.notifyListeners();
            return user;
        } catch (error) {
            console.error('Failed to get current user:', error);
            this.clearAuth();
            throw error;
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!(this.token && this.user);
    }

    /**
     * Get current user
     */
    getUser() {
        return this.user;
    }

    /**
     * Get access token
     */
    getToken() {
        return this.token;
    }
}

// Export singleton instance
export const authStore = new AuthStore();

// Initialize on import
if (typeof window !== 'undefined') {
    authStore.init();
}

export default authStore;
