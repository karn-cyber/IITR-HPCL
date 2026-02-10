/**
 * Alerts Service
 * Handles all alert preferences API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get alert preferences for current user
 * @returns {Promise<Object>} Alert preferences
 */
export async function getAlertPreferences() {
    return apiClient.get('/api/alerts/preferences');
}

/**
 * Update alert preferences
 * @param {Object} preferences - Alert preferences
 * @returns {Promise<Object>}
 */
export async function updateAlertPreferences(preferences) {
    return apiClient.put('/api/alerts/preferences', preferences);
}
