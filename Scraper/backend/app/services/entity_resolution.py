"""
Entity Resolution Service
Handles company name normalization, fuzzy matching, and deduplication.
"""

import re
from typing import Optional, Tuple, List

class EntityResolutionService:
    """
    Service for resolving company entities and deduplication.
    """
    
    # Common legal suffixes to remove for normalization
    LEGAL_SUFFIXES = [
        r'\bPvt\.? Ltd\.?', r'\bPrivate Limited\b',
        r'\bLtd\.?\b', r'\bLimited\b',
        r'\bCorp\.?\b', r'\bCorporation\b',
        r'\bInc\.?\b', r'\bIncorporated\b',
        r'\bLLC\b', r'\bLLP\b',
        r'\bCo\.?\b', r'\bCompany\b',
        r'\bInds\.?\b', r'\bIndustries\b',
        r'\bEnt\.?\b', r'\bEnterprises\b',
        r'\bGroup\b', r'\bHoldings\b'
    ]
    
    @classmethod
    def normalize_name(cls, name: str) -> str:
        """
        Normalize company name for comparison.
        1. Lowercase
        2. Remove legal suffixes
        3. Remove special characters
        4. Trim whitespace
        """
        if not name:
            return ""
            
        normalized = name.lower()
        
        # Remove suffixes
        for suffix in cls.LEGAL_SUFFIXES:
            normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
            
        # Remove special chars and extra whitespace
        normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized

    @classmethod
    def resolve_company(cls, db_instance, name: str, industry: Optional[str] = None, 
                       location: Optional[str] = None) -> int:
        """
        Find existing company or create new one.
        Returns company_id.
        """
        normalized_name = cls.normalize_name(name)
        
        # 1. Try exact match on normalized name
        conn = db_instance.get_connection()
        c = conn.cursor()
        
        c.execute("SELECT id, name FROM companies WHERE normalized_name = ?", (normalized_name,))
        result = c.fetchone()
        
        if result:
            conn.close()
            return result[0]
            
        # 2. Try fuzzy match (simple implementation for now: name contains or contained by)
        c.execute("SELECT id, name, normalized_name FROM companies")
        all_companies = c.fetchall()
        
        for comp_id, comp_name, comp_norm in all_companies:
            if not comp_norm:
                continue
                
            # Check if one is substring of other (with length check)
            if (normalized_name in comp_norm and len(normalized_name) > 4) or \
               (comp_norm in normalized_name and len(comp_norm) > 4):
                
                conn.close()
                return comp_id
        
        conn.close()
        
        # 3. If no match, create new company
        print(f"   ✨ New Entity: {name} (Norm: {normalized_name})")
        return db_instance.insert_company(name, industry, location)

    @staticmethod
    def calculate_similarity(s1: str, s2: str) -> float:
        """
        Calculate simple similarity ratio (0-1)
        Note: Python's difflib could be used here for better results
        """
        if not s1 or not s2:
            return 0.0
            
        s1 = s1.lower()
        s2 = s2.lower()
        
        if s1 == s2:
            return 1.0
            
        return 0.0 # Placeholder for more complex logic
