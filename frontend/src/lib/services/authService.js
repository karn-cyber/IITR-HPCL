/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Login with credentials
 * @param {Object} credentials - { email, password }
 * @returns {Promise<Object>} { access_token, user }
 */
export async function login(credentials) {
    return apiClient.post('/api/auth/login', credentials);
}

/**
 * Logout current user
 * @returns {Promise<Object>}
 */
export async function logout() {
    return apiClient.post('/api/auth/logout');
}

/**
 * Get current authenticated user
 * @returns {Promise<Object>} User object
 */
export async function getCurrentUser() {
    return apiClient.get('/api/auth/me');
}
