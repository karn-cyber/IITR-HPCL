"""
Territory and routing schemas
"""
from pydantic import BaseModel
from typing import List, Optional


class TerritoryResponse(BaseModel):
    """Territory information"""
    id: int
    name: str
    region: str
    depot: str
    coverage: List[str]
    activeLeads: int = 0
    assignedOfficers: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Mumbai West",
                "region": "Western",
                "depot": "Mumbai Depot",
                "coverage": ["Mumbai", "Thane", "Navi Mumbai"],
                "activeLeads": 15,
                "assignedOfficers": 3
            }
        }


class RouteLeadRequest(BaseModel):
    """Route lead to territory"""
    leadId: int
    territoryId: Optional[int] = None
    reason: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "leadId": 123,
                "territoryId": 1,
                "reason": "Geographic proximity"
            }
        }
