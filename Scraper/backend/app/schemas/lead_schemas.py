"""
Lead management schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LeadActionRequest(BaseModel):
    """Lead action request"""
    action: str  # ACCEPT, REJECT, CONVERT
    notes: Optional[str] = None
    nextFollowUp: Optional[datetime] = None
    estimatedDealValue: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "ACCEPT",
                "notes": "This looks promising, will follow up",
                "nextFollowUp": "2026-02-15T10:00:00Z",
                "estimatedDealValue": 5000000
            }
        }


class LeadNoteRequest(BaseModel):
    """Add note to lead"""
    note: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "note": "Called procurement head, showing interest"
            }
        }


class CompanyInfo(BaseModel):
    """Company information in lead detail"""
    name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    coordinates: Optional[dict] = None
    existingCustomer: Optional[bool] = None
    previousOrders: Optional[int] = None
    totalRevenue: Optional[float] = None


class LeadListItem(BaseModel):
    """Lead item in list view"""
    id: int
    timestamp: str
    company: str
    industry: Optional[str] = None
    location: Optional[str] = None
    primaryProduct: Optional[str] = None
    confidence: float
    reasonCodes: Optional[List[str]] = None
    status: str = "REVIEW_REQUIRED"
    source: str
    assignedTo: Optional[str] = None
    createdAt: str
    updatedAt: str


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    total: int
    page: int
    limit: int
    totalPages: int


class LeadListResponse(BaseModel):
    """Paginated lead list response"""
    leads: List[LeadListItem]
    pagination: PaginationInfo
    stats: Optional[dict] = None


class LeadDetailResponse(BaseModel):
    """Detailed lead response"""
    id: int
    company: CompanyInfo
    signal: dict
    products: Optional[List[dict]] = None
    scoring: Optional[dict] = None
    assignment: Optional[dict] = None
    actions: List[dict] = []
    notes: List[dict] = []
    documents: List[dict] = []
