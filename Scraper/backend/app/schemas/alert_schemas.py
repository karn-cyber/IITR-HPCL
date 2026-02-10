"""
Alert and notification schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional


class AlertPreferencesResponse(BaseModel):
    """User alert preferences"""
    userId: int
    emailEnabled: bool
    pushEnabled: bool
    minConfidence: float
    products: List[str]
    territories: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "userId": 1,
                "emailEnabled": True,
                "pushEnabled": False,
                "minConfidence": 0.7,
                "products": ["HSD", "FO"],
                "territories": ["Mumbai West"]
            }
        }


class AlertPreferencesUpdate(BaseModel):
    """Update alert preferences"""
    emailEnabled: Optional[bool] = None
    pushEnabled: Optional[bool] = None
    minConfidence: Optional[float] = None
    products: Optional[List[str]] = None
    territories: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "emailEnabled": True,
                "minConfidence": 0.8,
                "products": ["HSD", "FO", "BITUMEN"]
            }
        }
