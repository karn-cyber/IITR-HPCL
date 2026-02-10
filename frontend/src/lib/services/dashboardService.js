/**
 * Dashboard Service
 * Handles all dashboard and analytics-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get dashboard statistics
 * @param {Object} params - { start_date, end_date }
 * @returns {Promise<Object>} Dashboard stats
 */
export async function getDashboardStats(params = {}) {
    // Should pass { dateRange: '7d' | '30d' | 'all' }
    return apiClient.get('/api/dashboard/stats', params);
}

/**
 * Get performance metrics
 * @param {Object} params - { user_id, territory_id }
 * @returns {Promise<Object>} Performance metrics
 */
export async function getPerformanceMetrics(params = {}) {
    return apiClient.get('/api/dashboard/performance', params);
}
