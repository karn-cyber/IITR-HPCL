"""
Territory and routing router
"""
from fastapi import APIRouter, HTTPException, status, Depends
import json
from ..schemas.territory_schemas import TerritoryResponse, RouteLeadRequest
from ..models.database import db
from ..middleware.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/territories", tags=["Territories"])


@router.get("", response_model=list[TerritoryResponse])
async def get_territories(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all territories
    
    Requires authentication
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    # Get territories with stats
    c.execute('''
        SELECT t.id, t.name, t.region, t.depot, t.coverage_areas,
               COUNT(DISTINCT CASE WHEN l.status IN ('NEW', 'ACCEPTED') THEN l.id END) as active_leads,
               COUNT(DISTINCT u.id) as assigned_officers
        FROM territories t
        LEFT JOIN leads l ON l.territory = t.name
        LEFT JOIN users u ON u.territory_id = t.id
        GROUP BY t.id
        ORDER BY t.region, t.name
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    territories = []
    for row in rows:
        try:
            coverage = json.loads(row[4]) if row[4] else []
        except:
            coverage = []
        
        territories.append(TerritoryResponse(
            id=row[0],
            name=row[1],
            region=row[2],
            depot=row[3],
            coverage=coverage,
            activeLeads=row[5] or 0,
            assignedOfficers=row[6] or 0
        ))
    
    return territories


@router.post("/{territory_id}/route")
async def route_lead_to_territory(
    territory_id: int,
    request: RouteLeadRequest,
    current_user: dict = Depends(require_roles(['ADMIN', 'MANAGER']))
):
    """
    Route lead to territory (admin/manager only)
    
    Requires ADMIN or MANAGER role
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Get territory name
    c.execute('SELECT name FROM territories WHERE id = ?', (territory_id,))
    territory = c.fetchone()
    
    if not territory:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Territory {territory_id} not found"
        )
    
    territory_name = territory[0]
    
    # Check if lead exists
    c.execute('SELECT id FROM leads WHERE id = ?', (request.leadId,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead {request.leadId} not found"
        )
    
    # Update lead with territory
    from datetime import datetime
    c.execute('''
        UPDATE leads
        SET territory = ?, updated_at = ?
        WHERE id = ?
    ''', (territory_name, datetime.now().isoformat(), request.leadId))
    
    # Log the routing action
    c.execute('''
        INSERT INTO lead_actions (lead_id, user_id, action_type, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        request.leadId,
        current_user['id'],
        'ROUTE',
        request.reason or f'Routed to {territory_name}',
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "leadId": request.leadId,
        "territoryId": territory_id,
        "territoryName": territory_name,
        "message": f"Lead routed to {territory_name} successfully"
    }
