"""
Product Inference Service
Maps signal text and contexts to HPCL products with confidence scores.
"""

from typing import List, Dict, Any, Tuple
import re

class ProductInferenceService:
    """
    Service for inferring products from text signals.
    """
    
    # Product Knowledge Base
    # Maps keywords/contexts to Product Codes
    PRODUCT_RULES = {
        'FO': {
            'name': 'Furnace Oil',
            'keywords': ['furnace oil', 'fuel oil', 'bunker fuel', 'heavy oil', 'fo 180', 'fo 380'],
            'contexts': ['boiler', 'heating', 'power plant', 'thermal', 'kiln', 'furnace'],
            'min_confidence': 0.7
        },
        'LSHS': {
            'name': 'Low Sulphur Heavy Stock',
            'keywords': ['lshs', 'low sulphur heavy stock', 'low sulfur heavy stock'],
            'contexts': ['fertilizer', 'power generation', 'low emission', 'sulfur limit'],
            'min_confidence': 0.8
        },
        'HSD': {
            'name': 'High Speed Diesel',
            'keywords': ['hsd', 'high speed diesel', 'diesel', 'gas oil'],
            'contexts': ['transport', 'genset', 'generator', 'backup power', 'mining', 'fleet'],
            'min_confidence': 0.6
        },
        'LDO': {
            'name': 'Light Diesel Oil',
            'keywords': ['ldo', 'light diesel oil'],
            'contexts': ['pump', 'lift irrigation', 'small boiler', 'diesel engine'],
            'min_confidence': 0.75
        },
        'BITUMEN': {
            'name': 'Bitumen',
            'keywords': ['bitumen', 'asphalt', 'road tar', 'vg 30', 'vg 10', 'vg 40'],
            'contexts': ['road construction', 'highway', 'paving', 'infrastructure', 'waterproofing'],
            'min_confidence': 0.85
        },
        'HEXANE': {
            'name': 'Hexane',
            'keywords': ['hexane', 'food grade hexane'],
            'contexts': ['solvent extraction', 'vegetable oil', 'pharma', 'polymer'],
            'min_confidence': 0.8
        },
        'MTO': {
            'name': 'Mineral Turpentine Oil',
            'keywords': ['mto', 'mineral turpentine oil', 'white spirit'],
            'contexts': ['paint', 'varnish', 'dry cleaning', 'degreasing'],
            'min_confidence': 0.75
        },
        'JBO': {
            'name': 'Jute Batching Oil',
            'keywords': ['jbo', 'jute batching oil'],
            'contexts': ['jute', 'textile mill', 'fiber processing'],
            'min_confidence': 0.9
        }
    }
    
    @classmethod
    def infer_products(cls, text: str) -> List[Dict[str, Any]]:
        """
        Analyze text and return list of probable products.
        Returns: [
            {
                'code': 'FO',
                'name': 'Furnace Oil',
                'confidence': 0.85,
                'reasoning': 'Matched keywords: furnace oil; Context: boiler'
            },
            ...
        ]
        """
        results = []
        text_lower = text.lower()
        
        for code, rules in cls.PRODUCT_RULES.items():
            confidence = 0.0
            reasons = []
            
            # Check direct keywords (High impact)
            for kw in rules['keywords']:
                if kw in text_lower:
                    confidence += 0.6
                    reasons.append(f"Matched keyword: '{kw}'")
                    break  # Count only one keyword match per product
            
            # Check context keywords (Medium impact)
            for ctx in rules['contexts']:
                if ctx in text_lower:
                    confidence += 0.3
                    reasons.append(f"Matched context: '{ctx}'")
                    break # Count only one context match
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
            # Filter by minimum confidence
            if confidence >= 0.4: # Return low confidence matches too, for review
                results.append({
                    'code': code,
                    'name': rules['name'],
                    'confidence': round(confidence, 2),
                    'reasoning': '; '.join(reasons)
                })
        
        # Sort by confidence desc
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return results

    @classmethod
    def get_top_recommendations(cls, text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get top N product recommendations"""
        products = cls.infer_products(text)
        return products[:limit]
