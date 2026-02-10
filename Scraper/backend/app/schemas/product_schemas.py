"""
Product intelligence schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Optional


class ProductResponse(BaseModel):
    """Product information with rules"""
    code: str
    name: str
    category: str
    baseConfidenceRules: Dict[str, float]
    primaryKeywords: List[str]
    secondaryKeywords: List[str]
    negativeKeywords: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "HSD",
                "name": "High Speed Diesel",
                "category": "Fuels",
                "baseConfidenceRules": {
                    "explicitTenderWithVolume": 0.95,
                    "gensetInstallationAnnouncement": 0.85
                },
                "primaryKeywords": ["high speed diesel", "HSD", "diesel"],
                "secondaryKeywords": ["genset", "power backup"],
                "negativeKeywords": ["retail", "petrol pump"]
            }
        }


class ProductRuleUpdate(BaseModel):
    """Update product inference rules"""
    baseConfidenceRules: Optional[Dict[str, float]] = None
    primaryKeywords: Optional[List[str]] = None
    secondaryKeywords: Optional[List[str]] = None
    negativeKeywords: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "primaryKeywords": ["HSD", "diesel", "high speed diesel"],
                "secondaryKeywords": ["generator", "DG set"]
            }
        }
