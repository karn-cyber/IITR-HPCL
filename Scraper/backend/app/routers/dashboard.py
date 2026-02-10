"""
Dashboard and analytics router
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
from ..schemas.dashboard_schemas import (
    DashboardStatsResponse, DashboardPerformanceResponse,
    DashboardSummary, DashboardTrends,
    SignalProcessingMetrics, LeadQualityMetrics, CoverageMetrics
)
from ..models.database import db
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    dateRange: str = Query('7d', description="Date range: 7d, 30d, 90d, custom"),
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get dashboard statistics for the executive view
    
    Requires authentication
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    # Calculate date range
    end_date = datetime.now()
    if dateRange == 'all':
        start_date = datetime(2000, 1, 1) # Effectively all time
    elif dateRange == '7d':
        start_date = end_date - timedelta(days=7)
    elif dateRange == '30d':
        start_date = end_date - timedelta(days=30)
    elif dateRange == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = datetime.fromisoformat(startDate) if startDate else end_date - timedelta(days=7)
        end_date = datetime.fromisoformat(endDate) if endDate else datetime.now()
    
    start_date_str = start_date.date().isoformat()
    end_date_str = end_date.date().isoformat()
    
    # Get summary statistics
    total_leads = c.execute(
        "SELECT COUNT(*) FROM leads WHERE DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    high_confidence = c.execute(
        "SELECT COUNT(*) FROM leads WHERE confidence >= 0.9 AND DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    auto_assigned = c.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'AUTO_ASSIGNED' AND DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    estimated_value = c.execute(
        "SELECT COALESCE(SUM(estimated_value), 0) FROM leads WHERE DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    # Get leads by category (product)
    by_category_rows = c.execute('''
        SELECT products_mentioned, COUNT(*) as count
        FROM leads
        WHERE DATE(scraped_at) BETWEEN ? AND ?
        GROUP BY products_mentioned
        ORDER BY count DESC
        LIMIT 10
    ''', (start_date_str, end_date_str)).fetchall()
    
    by_category = {}
    for row in by_category_rows:
        product = row[0] if row[0] else "Unknown"
        try:
            import json
            products = json.loads(product)
            key = products[0] if products else "Unknown"
        except:
            key = "Unknown"
        by_category[key] = row[1]
    
    # Get leads by status
    by_status_rows = c.execute('''
        SELECT status, COUNT(*) as count
        FROM leads
        WHERE DATE(scraped_at) BETWEEN ? AND ?
        GROUP BY status
    ''', (start_date_str, end_date_str)).fetchall()
    
    by_status = {row[0] if row[0] else 'REVIEW_REQUIRED': row[1] for row in by_status_rows}
    
    # Get leads by confidence
    high = c.execute(
        "SELECT COUNT(*) FROM leads WHERE confidence >= 0.9 AND DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    medium = c.execute(
        "SELECT COUNT(*) FROM leads WHERE confidence >= 0.5 AND confidence < 0.9 AND DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    low = c.execute(
        "SELECT COUNT(*) FROM leads WHERE confidence < 0.5 AND DATE(scraped_at) BETWEEN ? AND ?",
        (start_date_str, end_date_str)
    ).fetchone()[0]
    
    by_confidence = {
        "High": high,
        "Medium": medium,
        "Low": low
    }
    
    # Get trends (leads per day for the last 7 days)
    # Always show last 7 days trend regardless of filter, or adapt? 
    # Usually trends chart is fixed window unless specified. 
    # I'll keep it as last 7 days for now as the UI expects it.
    leads_per_day = []
    for i in range(7):
        day = (end_date - timedelta(days=6-i)).date().isoformat()
        count = c.execute(
            "SELECT COUNT(*) FROM leads WHERE DATE(scraped_at) = ?",
            (day,)
        ).fetchone()[0]
        leads_per_day.append(count)
    
    # Calculate conversion rate
    total_actioned = c.execute(
        "SELECT COUNT(DISTINCT lead_id) FROM lead_actions WHERE created_at >= ?",
        (start_date_str,)
    ).fetchone()[0]
    conversion_rate = total_actioned / total_leads if total_leads > 0 else 0
    
    conn.close()
    
    return DashboardStatsResponse(
        summary=DashboardSummary(
            totalLeads=total_leads,
            highConfidence=high_confidence,
            autoAssigned=auto_assigned,
            estimatedValue=estimated_value
        ),
        byCategory=by_category,
        byStatus=by_status,
        byConfidence=by_confidence,
        trends=DashboardTrends(
            leadsPerDay=leads_per_day,
            conversionRate=conversion_rate,
            avgTimeToContact=2.5  # TODO: Calculate from data
        )
    )


@router.get("/performance", response_model=DashboardPerformanceResponse)
async def get_dashboard_performance(
    current_user: dict = Depends(get_current_user)
):
    """
    Get performance metrics for monitoring
    
    Requires authentication
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Get signal processing metrics
    total_scrapes = c.execute(
        "SELECT COUNT(*) FROM scrape_log"
    ).fetchone()[0]
    
    successful_scrapes = c.execute(
        "SELECT COUNT(*) FROM scrape_log WHERE status = 'success'"
    ).fetchone()[0]
    
    success_rate = successful_scrapes / total_scrapes if total_scrapes > 0 else 0
    
    # Get lead quality metrics
    total_actions = c.execute("SELECT COUNT(*) FROM lead_actions").fetchone()[0]
    accepted = c.execute(
        "SELECT COUNT(*) FROM lead_actions WHERE action_type = 'ACCEPT'"
    ).fetchone()[0]
    rejected = c.execute(
        "SELECT COUNT(*) FROM lead_actions WHERE action_type = 'REJECT'"
    ).fetchone()[0]
    converted = c.execute(
        "SELECT COUNT(*) FROM lead_actions WHERE action_type = 'CONVERT'"
    ).fetchone()[0]
    
    total_leads = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    acceptance_rate = accepted / total_leads if total_leads > 0 else 0
    rejection_rate = rejected / total_leads if total_leads > 0 else 0
    conversion_rate = converted / accepted if accepted > 0 else 0
    
    # Get coverage metrics
    active_sources = c.execute(
        "SELECT COUNT(DISTINCT source_name) FROM scrape_log WHERE scraped_at >= date('now', '-1 day')"
    ).fetchone()[0]
    
    total_sources = c.execute(
        "SELECT COUNT(DISTINCT domain) FROM source_registry"
    ).fetchone()[0]
    
    # Get geographic coverage
    locations = c.execute('''
        SELECT DISTINCT location FROM companies 
        WHERE location IS NOT NULL 
        LIMIT 10
    ''').fetchall()
    geographic_coverage = [loc[0] for loc in locations if loc[0]]
    
    conn.close()
    
    return DashboardPerformanceResponse(
        signalProcessing=SignalProcessingMetrics(
            avgDetectionTime=180.0,  # TODO: Calculate from actual data
            avgProcessingTime=45.0,
            successRate=success_rate
        ),
        leadQuality=LeadQualityMetrics(
            acceptanceRate=acceptance_rate,
            rejectionRate=rejection_rate,
            conversionRate=conversion_rate
        ),
        coverage=CoverageMetrics(
            sourcesActive=active_sources,
            sourcesTotal=total_sources or 10,
            geographicCoverage=geographic_coverage
        )
    )
