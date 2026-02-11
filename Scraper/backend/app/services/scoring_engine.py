"""
Scoring Engine
Calculates lead score based on multiple factors:
Score(L) = w1*Intent + w2*Freshness + w3*Size + w4*Geography
"""

from datetime import datetime
import math

class ScoringEngine:
    """
    Engine to calculate lead scores.
    """
    
    # Weights (must sum to 1.0)
    WEIGHTS = {
        'intent': 0.4,
        'freshness': 0.3,
        'size': 0.2,
        'geography': 0.1
    }
    
    # Intent Scores
    INTENT_SCORES = {
        'tender': 1.0,
        'procurement': 0.9,
        'expansion': 0.8,
        'commissioning': 0.75,
        'news': 0.5,
        'directory': 0.3
    }
    
    @staticmethod
    def calculate_freshness(scraped_at_iso: str) -> float:
        """
        Calculate freshness score using exponential decay.
        Score = e^(-lambda * days)
        lambda = 0.1 -> 90% after 1 day, 50% after 7 days
        """
        try:
            scraped_at = datetime.fromisoformat(scraped_at_iso)
            now = datetime.now()
            days_diff = (now - scraped_at).days
            
            # Ensure non-negative
            days_diff = max(0, days_diff)
            
            decay_rate = 0.1
            score = math.exp(-decay_rate * days_diff)
            return round(score, 2)
        except Exception:
            return 1.0 # Default to fresh if error
            
    @staticmethod
    def calculate_size_proxy(text: str) -> float:
        """
        Estimate company size from text mentions.
        Returns 0.0 to 1.0
        """
        text_lower = text.lower()
        
        # Keywords indicating scale
        huge_indicators = ['billion', 'mega project', 'massive expansion', 'integrated plant']
        large_indicators = ['million', 'crore', 'large scale', 'capacity expansion']
        medium_indicators = ['sme', 'mid-sized', 'growing']
        
        if any(i in text_lower for i in huge_indicators):
            return 1.0
        if any(i in text_lower for i in large_indicators):
            return 0.7
        if any(i in text_lower for i in medium_indicators):
            return 0.4
            
        return 0.2 # Default baseline
        
    @staticmethod
    def calculate_geo_score(lead_location: str, territory: str = None) -> float:
        """
        Calculate geographic relevance.
        Placeholder logic: 1.0 if match, 0.5 if unknown.
        """
        if not lead_location or not territory:
            return 0.5
            
        if territory.lower() in lead_location.lower():
            return 1.0
            
        return 0.5

    @classmethod
    def calculate_score(cls, signal_type: str, scraped_at: str, 
                       signal_text: str, location: str = None) -> dict:
        """
        Calculate composite score and return breakdown.
        """
        # 1. Intent Score
        intent_score = cls.INTENT_SCORES.get(signal_type.lower(), 0.5)
        
        # 2. Freshness Score
        freshness_score = cls.calculate_freshness(scraped_at)
        
        # 3. Size Proxy Score
        size_score = cls.calculate_size_proxy(signal_text)
        
        # 4. Geography Score
        geo_score = cls.calculate_geo_score(location)
        
        # Weighted Sum
        final_score = (
            (cls.WEIGHTS['intent'] * intent_score) +
            (cls.WEIGHTS['freshness'] * freshness_score) +
            (cls.WEIGHTS['size'] * size_score) +
            (cls.WEIGHTS['geography'] * geo_score)
        )
        
        return {
            'final_score': round(final_score, 2),
            'breakdown': {
                'intent': intent_score,
                'freshness': freshness_score,
                'size': size_score,
                'geography': geo_score
            }
        }
