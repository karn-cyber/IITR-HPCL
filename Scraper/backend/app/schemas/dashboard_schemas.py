"""
Dashboard and analytics schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Optional


class DashboardSummary(BaseModel):
    """Dashboard summary statistics"""
    totalLeads: int
    highConfidence: int
    autoAssigned: int
    estimatedValue: float


class DashboardTrends(BaseModel):
    """Dashboard trends"""
    leadsPerDay: List[int]
    conversionRate: float
    avgTimeToContact: float


class DashboardStatsResponse(BaseModel):
    """Dashboard stats response"""
    summary: DashboardSummary
    byCategory: Dict[str, int]
    byStatus: Dict[str, int]
    byConfidence: Dict[str, int]
    trends: Optional[DashboardTrends] = None


class SignalProcessingMetrics(BaseModel):
    """Signal processing metrics"""
    avgDetectionTime: float
    avgProcessingTime: float
    successRate: float


class LeadQualityMetrics(BaseModel):
    """Lead quality metrics"""
    acceptanceRate: float
    rejectionRate: float
    conversionRate: float


class CoverageMetrics(BaseModel):
    """Coverage metrics"""
    sourcesActive: int
    sourcesTotal: int
    geographicCoverage: List[str]


class DashboardPerformanceResponse(BaseModel):
    """Dashboard performance response"""
    signalProcessing: SignalProcessingMetrics
    leadQuality: LeadQualityMetrics
    coverage: CoverageMetrics
