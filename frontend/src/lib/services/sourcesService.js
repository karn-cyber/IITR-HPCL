/**
 * Sources Service
 * Handles all source management API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get all sources
 * @returns {Promise<Object>} { sources }
 */
export async function getSources() {
    return apiClient.get('/api/sources');
}

/**
 * Add new source (Admin only)
 * @param {Object} data - Source data
 * @returns {Promise<Object>}
 */
export async function addSource(data) {
    return apiClient.post('/api/sources', data);
}

/**
 * Trigger manual scrape for a source
 * @param {string|number} sourceId - Source ID
 * @returns {Promise<Object>}
 */
export async function triggerScrape(sourceId) {
    return apiClient.post(`/api/sources/${sourceId}/trigger`);
}
