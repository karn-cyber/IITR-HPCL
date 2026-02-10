"""
Feedback and learning schemas
"""
from pydantic import BaseModel
from typing import Optional


class FeedbackRequest(BaseModel):
    """Submit feedback on a lead"""
    leadId: int
    feedbackType: str  # QUALITY, RELEVANCE, ACCURACY
    rating: int  # 1-5
    comment: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "leadId": 123,
                "feedbackType": "RELEVANCE",
                "rating": 4,
                "comment": "Good lead, but product match could be better"
            }
        }


class FeedbackAnalytics(BaseModel):
    """Feedback analytics for admin"""
    totalFeedback: int
    averageRating: float
    qualityScore: float
    relevanceScore: float
    accuracyScore: float
    improvementAreas: list[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "totalFeedback": 150,
                "averageRating": 3.8,
                "qualityScore": 4.1,
                "relevanceScore": 3.7,
                "accuracyScore": 3.6,
                "improvementAreas": ["Product matching", "Confidence scoring"]
            }
        }
