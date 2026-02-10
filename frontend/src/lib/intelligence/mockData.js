/**
 * Mock Data Generator for HPCL Lead Intelligence
 * Generates 200+ samples across 12 product categories
 */

const COMPANY_NAMES = [
    "Reliance Industries", "Adani Enterprises", "Tata Steel", "JSW Steel", "Vedanta Ltd",
    "Dalmia Bharat", "UltraTech Cement", "Asian Paints", "Pidilite Industries", "Coromandel International",
    "Grasim Industries", "Ambuja Cements", "Shree Cement", "Hindalco", "Larsen & Toubro",
    "NTPC", "BHEL", "NHPC", "Power Grid", "Coal India", "ONGC", "IOCL", "BPCL", "HPCL (Internal Testing)",
    "Infosys Data Center", "Wipro Cloud", "Apollo Hospitals", "Max Healthcare", "Marriott Hotels",
    "Taj Group", "Hyatt Regency", "DLF Infrastructure", "Lodha Group", "Godrej Properties"
];

const INDUSTRIES = [
    "Steel & Metal", "Cement", "Chemical", "Paper & Pulp", "Sugar", "Distillery",
    "Fertilizer", "Pharmaceutical", "Glass", "Ceramic", "Textile", "Rubber", "Power"
];

const PRODUCT_CODES = ["HSD", "LDO", "FO", "BITUMEN", "BUNKER", "HEXANE", "PROPYLENE", "JBO", "SOLVENT_1425", "MTO_2445", "SULPHUR", "SKO_NON_PDS"];

export function generateMockLeads(count = 200) {
    const leads = [];
    for (let i = 0; i < count; i++) {
        // Use index i to make selections predictable based on index
        // This ensures LEAD-1000 is always the same "Reliance" entry, etc.
        const companyIndex = i % COMPANY_NAMES.length;
        const industryIndex = (i + 2) % INDUSTRIES.length;
        const productIndex = (i + 5) % PRODUCT_CODES.length;
        const locationIndex = (i + 3) % 7;
        const typeChoiceIndex = (i * 7) % 10; // Values 0-9

        const company = COMPANY_NAMES[companyIndex];
        const industry = INDUSTRIES[industryIndex];
        const productCode = PRODUCT_CODES[productIndex];

        let signalType = 'NEWS';
        if (typeChoiceIndex > 7) signalType = 'TENDER';
        else if (typeChoiceIndex > 4) signalType = 'WEB_STORY';

        const hasCapacity = (i % 2) === 0;
        const hasHighConfidence = (i % 3) !== 0;

        const properties = {};
        if (hasCapacity) properties.capacityMentioned = true;
        if ((i % 5) === 0) properties.urgencyIndicators = true;
        if ((i % 7) === 0) properties.existingHPCLCustomer = true;

        const baseSignal = {
            text: `Stable detection for ${company} in ${industry} sector showing interest in ${productCode}`,
            type: signalType,
            hasVolume: (i % 4) === 0,
            hasCapacity: hasCapacity,
            hasHighConfidenceIndustry: hasHighConfidence,
            properties: properties
        };

        const result = calculateLeadConfidence(baseSignal, productCode);

        leads.push({
            id: `LEAD-${1000 + i}`,
            // Fixed timestamp based on ID to remain stable
            timestamp: new Date(2026, i % 12, (i % 28) + 1).toISOString(),
            company,
            industry,
            location: ["Mumbai", "Ahmedabad", "Pune", "Chennai", "Kolkata", "Delhi", "Visakhapatnam"][locationIndex],
            primaryProduct: productCode,
            confidence: result.finalConfidence,
            reasonCodes: result.reasonCodes,
            status: result.finalConfidence >= 0.90 ? "AUTO_ASSIGNED" : (result.finalConfidence >= 0.75 ? "QUALIFIED" : "REVIEW_REQUIRED"),
            source: signalType === 'TENDER' ? 'GeM Portal' : (signalType === 'NEWS' ? 'Financial Express' : 'Company Website')
        });
    }
    // Return sorted but derived from stable base
    return [...leads].sort((a, b) => b.confidence - a.confidence);
}

export function getLeadById(id) {
    const numericId = parseInt(id.split('-')[1]);
    const index = numericId - 1000;
    if (isNaN(index) || index < 0) return null;

    // We recreate the specific lead based on its index i
    const leads = generateMockLeads(index + 1);
    const lead = leads.find(l => l.id === id);
    return lead;
}

import { calculateLeadConfidence } from './engine';
