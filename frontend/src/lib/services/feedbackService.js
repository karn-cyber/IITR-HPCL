/**
 * Feedback Service
 * Handles all feedback-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Submit feedback
 * @param {Object} feedback - Feedback data
 * @returns {Promise<Object>}
 */
export async function submitFeedback(feedback) {
    return apiClient.post('/api/feedback', feedback);
}

/**
 * Get feedback analytics (Admin only)
 * @param {Object} params - { start_date, end_date }
 * @returns {Promise<Object>} Feedback analytics
 */
export async function getFeedbackAnalytics(params = {}) {
    return apiClient.get('/api/feedback/analytics', params);
}
