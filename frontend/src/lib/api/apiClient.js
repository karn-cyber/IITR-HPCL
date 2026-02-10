/**
 * API Client for HPCL Lead Intelligence Backend
 * Handles all HTTP requests with automatic JWT token attachment
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    /**
     * Get authorization headers with JWT token
     */
    getHeaders(customHeaders = {}) {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Handle API response
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));

            // Handle authentication errors
            if (response.status === 401) {
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
                throw new Error('Authentication required. Please log in again.');
            }

            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`);

        // Add query parameters
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    }

    /**
     * Upload file (multipart/form-data)
     */
    async upload(endpoint, formData) {
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers, // Don't set Content-Type for FormData
            body: formData
        });

        return this.handleResponse(response);
    }
}

// Export singleton instance
export const apiClient = new APIClient(API_BASE_URL);
export default apiClient;
