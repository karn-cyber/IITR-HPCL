"""
Alert and notification router
"""
from fastapi import APIRouter, HTTPException, status, Depends
import json
from datetime import datetime
from ..schemas.alert_schemas import AlertPreferencesResponse, AlertPreferencesUpdate
from ..models.database import db
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/preferences", response_model=AlertPreferencesResponse)
async def get_alert_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's alert preferences
    
    Requires authentication
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    # Try to get existing preferences
    c.execute('''
        SELECT email_enabled, push_enabled, min_confidence, products, territories
        FROM users
        WHERE id = ?
    ''', (current_user['id'],))
    
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    
    try:
        products = json.loads(row[3]) if row[3] else []
    except:
        products = []
    
    try:
        territories = json.loads(row[4]) if row[4] else []
    except:
        territories = []
    
    return AlertPreferencesResponse(
        userId=current_user['id'],
        emailEnabled=row[0] if row[0] is not None else True,
        pushEnabled=row[1] if row[1] is not None else False,
        minConfidence=row[2] if row[2] is not None else 0.7,
        products=products,
        territories=territories
    )


@router.put("/preferences")
async def update_alert_preferences(
    preferences: AlertPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update alert preferences
    
    Requires authentication
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Build update query
    updates = []
    params = []
    
    if preferences.emailEnabled is not None:
        updates.append('email_enabled = ?')
        params.append(1 if preferences.emailEnabled else 0)
    
    if preferences.pushEnabled is not None:
        updates.append('push_enabled = ?')
        params.append(1 if preferences.pushEnabled else 0)
    
    if preferences.minConfidence is not None:
        if preferences.minConfidence < 0 or preferences.minConfidence > 1:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="minConfidence must be between 0 and 1"
            )
        updates.append('min_confidence = ?')
        params.append(preferences.minConfidence)
    
    if preferences.products is not None:
        updates.append('products = ?')
        params.append(json.dumps(preferences.products))
    
    if preferences.territories is not None:
        updates.append('territories = ?')
        params.append(json.dumps(preferences.territories))
    
    if not updates:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Execute update
    params.append(current_user['id'])
    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "userId": current_user['id'],
        "message": "Alert preferences updated successfully"
    }
