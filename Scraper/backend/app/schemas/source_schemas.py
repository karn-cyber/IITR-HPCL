"""
Source management schemas
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class SourceResponse(BaseModel):
    """Source information"""
    id: int
    name: str
    type: str
    url: str
    category: str
    trustScore: int
    active: bool
    lastScraped: Optional[str] = None
    itemsFound: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "GeM Portal",
                "type": "TENDER",
                "url": "https://gem.gov.in",
                "category": "Government Tenders",
                "trustScore": 95,
                "active": True,
                "lastScraped": "2026-02-10T01:30:00Z",
                "itemsFound": 15
            }
        }


class SourceCreateRequest(BaseModel):
    """Create new source"""
    name: str
    type: str  # TENDER, NEWS, DIRECTORY
    url: str
    category: str
    trustScore: int = 80
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Industry News Portal",
                "type": "NEWS",
                "url": "https://example.com",
                "category": "Industry News",
                "trustScore": 85
            }
        }
