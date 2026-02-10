"""
Lead management router
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
import json
from ..schemas.lead_schemas import (
    LeadListResponse, LeadDetailResponse, LeadActionRequest,
    LeadNoteRequest, LeadListItem, PaginationInfo, CompanyInfo
)
from ..models.database import db
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=LeadListResponse)
async def get_leads(
    page: Optional[int] = Query(None, ge=1),
    skip: Optional[int] = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=100),
    filter: Optional[str] = Query(None, description="Status filter: ALL, AUTO_ASSIGNED, QUALIFIED, REVIEW_REQUIRED"),
    search: Optional[str] = Query(None, description="Search by company name or product"),
    minConfidence: Optional[float] = Query(None, ge=0, le=1),
    productCode: Optional[str] = None,
    location: Optional[str] = None,
    sortBy: str = Query('confidence', description="Sort field: confidence, timestamp, company"),
    sortOrder: str = Query('desc', description="Sort order: asc, desc"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of leads with filtering and sorting
    
    Supports both page-based (page) and offset-based (skip) pagination.
    If skip is provided, it takes precedence over page.
    
    Requires authentication
    """
    # Convert skip to page if provided
    if skip is not None:
        calculated_page = (skip // limit) + 1
    elif page is not None:
        calculated_page = page
    else:
        calculated_page = 1
    
    result = db.get_leads_paginated(
        page=calculated_page,
        limit=limit,
        filter_status=filter if filter != 'ALL' else None,
        search=search,
        min_confidence=minConfidence,
        product_code=productCode,
        location=location,
        sort_by=sortBy,
        sort_order=sortOrder
    )
    
    # Transform to response format
    leads = []
    for lead in result['leads']:
        # Parse products if JSON string
        products_mentioned = None
        if lead.get('products_mentioned'):
            try:
                products_mentioned = json.loads(lead['products_mentioned'])
            except:
                products_mentioned = []
        
        leads.append(LeadListItem(
            id=lead['id'],
            timestamp=lead['scraped_at'],
            company=lead['company_name'],
            industry=lead.get('industry'),
            location=lead.get('location'),
            primaryProduct=products_mentioned[0] if products_mentioned and len(products_mentioned) > 0 else None,
            confidence=lead['confidence'],
            reasonCodes=[],  # TODO: Parse from scoring field
            status=lead.get('status', 'REVIEW_REQUIRED'),
            source=lead['source_name'],
            assignedTo=lead.get('assigned_to'),
            createdAt=lead['scraped_at'],
            updatedAt=lead['scraped_at']
        ))
    
    return LeadListResponse(
        leads=leads,
        pagination=PaginationInfo(**result['pagination']),
        stats=None  # TODO: Add stats
    )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead_detail(
    lead_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific lead
    
    Requires authentication
    """
    lead = db.get_lead_by_id(lead_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Parse JSON fields
    products_mentioned = []
    if lead.get('products_mentioned'):
        try:
            products_mentioned = json.loads(lead['products_mentioned'])
        except:
            pass
    
    scoring = {}
    if lead.get('scoring'):
        try:
            scoring = json.loads(lead['scoring'])
        except:
            pass
    
    history = {}
    if lead.get('history'):
        try:
            history = json.loads(lead['history'])
        except:
            pass
    
    # Build company info
    company = CompanyInfo(
        name=lead['company_name'],
        industry=lead.get('industry'),
        location=lead.get('location'),
        coordinates={'lat': lead.get('lat'), 'lng': lead.get('lng')} if lead.get('lat') else None,
        existingCustomer=bool(lead.get('existing_customer')),
        previousOrders=history.get('totalOrders', 0) if history else None,
        totalRevenue=history.get('totalRevenue', 0) if history else None
    )
    
    # Build signal info
    signal = {
        'type': lead['signal_type'],
        'source': lead['source_name'],
        'sourceUrl': lead.get('source_url'),
        'detectedAt': lead['scraped_at'],
        'rawText': lead.get('signal_text', '')[:500] + '...' if lead.get('signal_text') else '',
        'extractedEntities': {}  # TODO: Add entity extraction
    }
    
    # Build products list
    products = []
    for product in products_mentioned:
        products.append({
            'code': product,
            'name': product,  # TODO: Map to product names
            'confidence': lead['confidence'],
            'reasoning': 'Product mentioned in signal'
        })
    
    # Build assignment info
    assignment = {
        'status': lead.get('status', 'REVIEW_REQUIRED'),
        'assignedTo': lead.get('assigned_to'),
        'assignedAt': None,  # TODO: Track assignment timestamp
        'territory': lead.get('territory')
    }
    
    return LeadDetailResponse(
        id=lead['id'],
        company=company,
        signal=signal,
        products=products,
        scoring=scoring or {
            'finalScore': lead['confidence'],
            'breakdown': {}
        },
        assignment=assignment,
        actions=lead.get('actions', []),
        notes=lead.get('notes', []),
        documents=lead.get('documents', [])
    )


@router.post("/{lead_id}/action")
async def add_lead_action(
    lead_id: int,
    action: LeadActionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Record sales officer actions (accept/reject/convert)
    
    Requires authentication
    """
    # Verify lead exists
    lead = db.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Add action
    action_id = db.add_lead_action(
        lead_id=lead_id,
        user_id=current_user['id'],
        action_type=action.action,
        notes=action.notes,
        next_follow_up=action.nextFollowUp.isoformat() if action.nextFollowUp else None,
        estimated_deal_value=action.estimatedDealValue
    )
    
    # Get updated status
    updated_lead = db.get_lead_by_id(lead_id)
    
    return {
        "success": True,
        "leadId": lead_id,
        "updatedStatus": updated_lead.get('status'),
        "message": f"Lead {action.action.lower()}ed successfully"
    }


@router.post("/{lead_id}/notes")
async def add_lead_note(
    lead_id: int,
    note_request: LeadNoteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add notes/comments to a lead
    
    Requires authentication
    """
    # Verify lead exists
    lead = db.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Add note
    note_id = db.add_lead_note(
        lead_id=lead_id,
        user_id=current_user['id'],
        note=note_request.note
    )
    
    return {
        "success": True,
        "noteId": note_id,
        "message": "Note added successfully"
    }


@router.post("/{lead_id}/documents")
async def upload_lead_document(
    lead_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Upload documents (quotes, proposals) related to a lead
    
    TODO: Implement file upload handling
    Requires authentication
    """
    # Verify lead exists
    lead = db.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # TODO: Implement file upload
    return {
        "success": True,
        "message": "Document upload endpoint - to be implemented"
    }
