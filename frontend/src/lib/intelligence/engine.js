/**
 * HPCL B2B Lead Intelligence Engine
 * Implements the logic from Section 4 & 5 of Technical Documentation
 */

export const PRODUCTS = [
    {
        code: "HSD",
        name: "High Speed Diesel",
        baseConfidenceRules: {
            explicitTenderWithVolume: 0.95,
            gensetInstallationAnnouncement: 0.85,
            facilityExpansionWithPowerMention: 0.75,
            industryWithCapacitySignal: 0.65,
            industryOnlyHighConfidence: 0.45,
            industryOnlyMedium: 0.35,
        },
        primaryKeywords: ["high speed diesel", "HSD", "diesel genset", "DG set", "captive power"],
        secondaryKeywords: ["power backup", "generator fuel", "standby power"],
        negativeKeywords: ["retail", "petrol pump", "automobile"],
        scoringFactors: {
            capacityMentioned: 0.15,
            multipleGensets: 0.10,
            urgencyIndicators: 0.10,
            existingHPCLCustomer: 0.05,
        }
    },
    {
        code: "FO",
        name: "Furnace Oil",
        baseConfidenceRules: {
            explicitFOTenderWithVolume: 0.95,
            boilerInstallationWithCapacity: 0.90,
            furnaceInHighConfidenceIndustry: 0.85,
            plantExpansionWithBoilerMention: 0.80,
            steamRequirementWithIndustry: 0.70,
            highConfidenceIndustryWithFacility: 0.55,
            industryOnlySignal: 0.40,
        },
        primaryKeywords: ["furnace oil", "FO", "heavy fuel oil", "HFO", "LSHS"],
        secondaryKeywords: ["boiler fuel", "industrial boiler", "steam generation", "process heating"],
        negativeKeywords: ["domestic", "household", "small scale"],
        scoringFactors: {
            capacityVolumeSpecified: 0.15,
            multipleBoilersOrFurnaces: 0.10,
            environmentalClearanceObtained: 0.08,
            commissioningTimelineNear: 0.10,
            existingHPCLRelationship: 0.05,
        },
        disqualifiers: {
            coalOnlyMention: -0.30,
            gasBasedOnly: -0.40
        }
    },
    {
        code: "BITUMEN",
        name: "Bitumen",
        baseConfidenceRules: {
            governmentTenderWithBitumenSpec: 0.95,
            highwayProjectAnnouncement: 0.90,
            hotMixPlantCommissioning: 0.85,
            roadProjectWithLength: 0.80,
            contractorAwardedProject: 0.75,
            infrastructureProjectWithPaving: 0.70,
            realEstateWithRoadComponent: 0.60,
            industryOnlyWithCue: 0.45,
        },
        primaryKeywords: ["bitumen", "asphalt", "VG 30", "VG 40", "paving grade"],
        secondaryKeywords: ["road construction", "highway project", "paving work", "road surfacing"],
        negativeKeywords: ["patch work", "minor maintenance"],
        scoringFactors: {
            projectValueHigh: 0.10,
            multiYearContract: 0.10,
            urgentTimeline: 0.08,
            NHAIorPWDProject: 0.12,
            existingHPCLCustomer: 0.05,
        }
    }
];

export function calculateLeadConfidence(signal, productCode) {
    const product = PRODUCTS.find(p => p.code === productCode);
    if (!product) return { finalConfidence: 0.30, reasonCodes: ["Product not found"] };

    const signalText = signal.text.toLowerCase();

    // 1. Check Disqualifiers
    if (product.disqualifiers) {
        for (const [key, penalty] of Object.entries(product.disqualifiers)) {
            if (signalText.includes(key.replace(/([A-Z])/g, ' $1').toLowerCase().trim())) {
                // simplified check mapping camelCase to space
            }
        }
        // Specific negative keywords
        for (const neg of product.negativeKeywords) {
            if (signalText.includes(neg.toLowerCase())) {
                return { finalConfidence: 0.20, status: "DISCARDED", reasonCodes: ["Matched negative keyword: " + neg] };
            }
        }
    }

    // 2. Determine Base Confidence
    let baseConfidence = 0.30;
    let matchedRule = "defaultBaseline";

    // In a real system, this would be complex NLP. Here we use rule matching based on signal properties.
    if (signal.type === 'TENDER' && signal.hasVolume) {
        baseConfidence = product.baseConfidenceRules.explicitTenderWithVolume || product.baseConfidenceRules.explicitFOTenderWithVolume || product.baseConfidenceRules.governmentTenderWithBitumenSpec || 0.95;
        matchedRule = "explicitTenderWithVolume";
    } else if (signal.hasCapacity && signal.hasHighConfidenceIndustry) {
        baseConfidence = product.baseConfidenceRules.boilerInstallationWithCapacity || product.baseConfidenceRules.gensetInstallationAnnouncement || 0.85;
        matchedRule = "installationWithCapacity";
    } else if (signal.hasHighConfidenceIndustry) {
        baseConfidence = product.baseConfidenceRules.industryOnlyHighConfidence || product.baseConfidenceRules.furnaceInHighConfidenceIndustry || 0.55;
        matchedRule = "highConfidenceIndustry";
    }

    // 3. Apply Scoring factors (Modifiers)
    let modifiers = 0;
    const reasonCodes = [`Base: ${matchedRule} (${baseConfidence})`];

    if (product.scoringFactors) {
        for (const [key, value] of Object.entries(product.scoringFactors)) {
            if (signal.properties && signal.properties[key]) {
                modifiers += parseFloat(value);
                reasonCodes.push(`Modifier: ${key} (+${value})`);
            }
        }
    }

    let finalConfidence = baseConfidence + modifiers;

    // Constraints
    finalConfidence = Math.max(0.30, Math.min(0.95, finalConfidence));
    finalConfidence = Math.round(finalConfidence * 100) / 100;

    return {
        finalConfidence,
        reasonCodes,
        baseConfidence,
        modifiers
    };
}
