/**
 * Products Service
 * Handles all product-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get all products
 * @returns {Promise<Object>} { products }
 */
export async function getProducts() {
    return apiClient.get('/api/products');
}

/**
 * Update product rules (Admin only)
 * @param {string} productCode - Product code
 * @param {Object} rules - Product rules
 * @returns {Promise<Object>}
 */
export async function updateProductRules(productCode, rules) {
    return apiClient.put(`/api/products/${productCode}/rules`, rules);
}
