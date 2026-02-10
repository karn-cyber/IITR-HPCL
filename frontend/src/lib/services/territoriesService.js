/**
 * Territories Service
 * Handles all territory-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get all territories
 * @returns {Promise<Object>} { territories }
 */
export async function getTerritories() {
    return apiClient.get('/api/territories');
}

/**
 * Route lead to territory
 * @param {string|number} territoryId - Territory ID
 * @param {Object} data - { lead_id, assign_to_user, notes }
 * @returns {Promise<Object>}
 */
export async function routeLeadToTerritory(territoryId, data) {
    return apiClient.post(`/api/territories/${territoryId}/route`, data);
}
