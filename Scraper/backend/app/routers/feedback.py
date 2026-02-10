"""
Feedback and learning router
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from ..schemas.feedback_schemas import FeedbackRequest, FeedbackAnalytics
from ..models.database import db
from ..middleware.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on a lead
    
    Requires authentication
    """
    # Validate rating
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Validate feedback type
    valid_types = ['QUALITY', 'RELEVANCE', 'ACCURACY']
    if feedback.feedbackType not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feedback type must be one of: {', '.join(valid_types)}"
        )
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # Check if lead exists
    c.execute('SELECT id FROM leads WHERE id = ?', (feedback.leadId,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {feedback.leadId} not found"
        )
    
    # Insert feedback
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO feedback (lead_id, user_id, feedback_type, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        feedback.leadId,
        current_user['id'],
        feedback.feedbackType,
        feedback.rating,
        feedback.comment,
        now
    ))
    
    feedback_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "feedbackId": feedback_id,
        "message": "Feedback submitted successfully"
    }


@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    current_user: dict = Depends(require_roles(['ADMIN', 'MANAGER']))
):
    """
    Get feedback analytics (admin/manager only)
    
    Requires ADMIN or MANAGER role
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    # Get overall stats
    c.execute('''
        SELECT COUNT(*) as total,
               AVG(rating) as avg_rating,
               AVG(CASE WHEN feedback_type = 'QUALITY' THEN rating END) as quality,
               AVG(CASE WHEN feedback_type = 'RELEVANCE' THEN rating END) as relevance,
               AVG(CASE WHEN feedback_type = 'ACCURACY' THEN rating END) as accuracy
        FROM feedback
    ''')
    
    row = c.fetchone()
    
    if not row:
        conn.close()
        return FeedbackAnalytics(
            totalFeedback=0,
            averageRating=0.0,
            qualityScore=0.0,
            relevanceScore=0.0,
            accuracyScore=0.0,
            improvementAreas=[]
        )
    
    total = row[0] or 0
    avg_rating = row[1] or 0.0
    quality = row[2] or 0.0
    relevance = row[3] or 0.0
    accuracy = row[4] or 0.0
    
    # Determine improvement areas (scores below 4.0)
    improvement_areas = []
    if quality < 4.0:
        improvement_areas.append("Lead quality")
    if relevance < 4.0:
        improvement_areas.append("Product matching")
    if accuracy < 4.0:
        improvement_areas.append("Confidence scoring")
    
    conn.close()
    
    return FeedbackAnalytics(
        totalFeedback=total,
        averageRating=round(avg_rating, 2),
        qualityScore=round(quality, 2),
        relevanceScore=round(relevance, 2),
        accuracyScore=round(accuracy, 2),
        improvementAreas=improvement_areas
    )
