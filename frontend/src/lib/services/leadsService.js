/**
 * Leads Service
 * Handles all lead-related API calls
 */

import { apiClient } from '../api/apiClient';

/**
 * Get leads with filters and pagination
 * @param {Object} params - { skip, limit, signal_type, min_confidence }
 * @returns {Promise<Object>} { total, skip, limit, leads }
 */
export async function getLeads(params = {}) {
    return apiClient.get('/api/leads', params);
}

/**
 * Get lead by ID
 * @param {string|number} leadId - Lead ID
 * @returns {Promise<Object>} Lead object with full details
 */
export async function getLeadById(leadId) {
    return apiClient.get(`/api/leads/${leadId}`);
}

/**
 * Add action to lead
 * @param {string|number} leadId - Lead ID
 * @param {Object} data - { action_type, notes }
 * @returns {Promise<Object>}
 */
export async function addLeadAction(leadId, data) {
    return apiClient.post(`/api/leads/${leadId}/action`, data);
}

/**
 * Add note to lead
 * @param {string|number} leadId - Lead ID
 * @param {Object} data - { note_text, is_internal }
 * @returns {Promise<Object>}
 */
export async function addLeadNote(leadId, data) {
    return apiClient.post(`/api/leads/${leadId}/notes`, data);
}

/**
 * Upload document to lead
 * @param {string|number} leadId - Lead ID
 * @param {File} file - File to upload
 * @param {string} documentType - Document type (proposal, contract, correspondence)
 * @param {string} description - Description
 * @returns {Promise<Object>}
 */
export async function uploadLeadDocument(leadId, file, documentType, description) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('description', description);

    return apiClient.upload(`/api/leads/${leadId}/documents`, formData);
}
