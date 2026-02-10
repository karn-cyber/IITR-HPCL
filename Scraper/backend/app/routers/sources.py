"""
Source management router
"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from ..schemas.source_schemas import SourceResponse, SourceCreateRequest
from ..models.database import db
from ..middleware.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/sources", tags=["Sources"])


@router.get("", response_model=list[SourceResponse])
async def get_sources(
   current_user: dict = Depends(get_current_user)
):
    """
    Get all configured sources
    
    Requires authentication
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    # Get sources from registry
    c.execute('''
        SELECT sr.id, sr.domain, sr.category, sr.trust_score, sr.last_checked,
               sl.source_name, sl.source_type, sl.items_found, sl.scraped_at
        FROM source_registry sr
        LEFT JOIN (
            SELECT source_name, source_type, items_found, scraped_at,
                   ROW_NUMBER() OVER (PARTITION BY source_name ORDER BY scraped_at DESC) as rn
            FROM scrape_log
        ) sl ON sr.domain LIKE '%' || sl.source_name || '%' AND sl.rn = 1
        ORDER BY sr.trust_score DESC, sr.domain
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    sources = []
    for row in rows:
        sources.append(SourceResponse(
            id=row[0],
            name=row[5] or row[1],  # source_name or domain
            type=row[6] or "UNKNOWN",  # source_type
            url=row[1],  # domain
            category=row[2],
            trustScore=row[3],
            active=True,  # TODO: Add active flag to registry
            lastScraped=row[8],  # scraped_at
            itemsFound=row[7]  # items_found
        ))
    
    return sources


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreateRequest,
    current_user: dict = Depends(require_roles(['ADMIN']))
):
    """
    Add new source (admin only)
    
    Requires ADMIN role
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Check if source already exists
    c.execute('SELECT id FROM source_registry WHERE domain = ?', (source.url,))
    if c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source with this URL already exists"
        )
    
    # Insert new source
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO source_registry (domain, category, trust_score, robots_compliant, last_checked)
        VALUES (?, ?, ?, ?, ?)
    ''', (source.url, source.category, source.trustScore, True, now))
    
    source_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "sourceId": source_id,
        "message": f"Source '{source.name}' added successfully"
    }


@router.post("/{source_id}/trigger")
async def trigger_source_fetch(
    source_id: int,
    current_user: dict = Depends(require_roles(['ADMIN', 'MANAGER']))
):
    """
    Manually trigger scrape for a source
    
    Requires ADMIN or MANAGER role
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Check if source exists
    c.execute('SELECT domain FROM source_registry WHERE id = ?', (source_id,))
    source = c.fetchone()
    
    if not source:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found"
        )
    
    conn.close()
    
    # TODO: Implement actual scraper triggering logic
    # For now, return success message
    
    return {
        "success": True,
        "sourceId": source_id,
        "message": "Scrape triggered successfully",
        "note": "Manual scraping to be implemented"
    }
