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
        const company = COMPANY_NAMES[Math.floor(Math.random() * COMPANY_NAMES.length)];
        const industry = INDUSTRIES[Math.floor(Math.random() * INDUSTRIES.length)];
        const productCode = PRODUCT_CODES[Math.floor(Math.random() * PRODUCT_CODES.length)];

        // Randomize score components
        const typeChoice = Math.random();
        let signalType = 'NEWS';
        if (typeChoice > 0.8) signalType = 'TENDER';
        else if (typeChoice > 0.6) signalType = 'WEB_STORY';

        const hasCapacity = Math.random() > 0.5;
        const hasHighConfidence = Math.random() > 0.3;

        const properties = {};
        if (hasCapacity) properties.capacityMentioned = true;
        if (Math.random() > 0.7) properties.urgencyIndicators = true;
        if (Math.random() > 0.8) properties.existingHPCLCustomer = true;

        const baseSignal = {
            text: `Detection for ${company} in ${industry} sector showing interest in ${productCode}`,
            type: signalType,
            hasVolume: Math.random() > 0.7,
            hasCapacity: hasCapacity,
            hasHighConfidenceIndustry: hasHighConfidence,
            properties: properties
        };

        const result = calculateLeadConfidence(baseSignal, productCode);

        leads.push({
            id: `LEAD-${1000 + i}`,
            timestamp: new Date(Date.now() - Math.floor(Math.random() * 1000000000)).toISOString(),
            company,
            industry,
            location: ["Mumbai", "Ahmedabad", "Pune", "Chennai", "Kolkata", "Delhi", "Visakhapatnam"][Math.floor(Math.random() * 7)],
            primaryProduct: productCode,
            confidence: result.finalConfidence,
            reasonCodes: result.reasonCodes,
            status: result.finalConfidence >= 0.90 ? "AUTO_ASSIGNED" : (result.finalConfidence >= 0.75 ? "QUALIFIED" : "REVIEW_REQUIRED"),
            source: signalType === 'TENDER' ? 'GeM Portal' : (signalType === 'NEWS' ? 'Financial Express' : 'Company Website')
        });
    }
    return leads.sort((a, b) => b.confidence - a.confidence);
}

import { calculateLeadConfidence } from './engine';
