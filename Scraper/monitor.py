#!/usr/bin/env python3
"""
HP-Pulse Monitoring Dashboard
View scraper statistics and recent activity
"""

import sqlite3
from datetime import datetime, timedelta
from tabulate import tabulate

def show_dashboard():
    """Display comprehensive scraper dashboard"""
    
    try:
        conn = sqlite3.connect('hp_pulse.db')
        c = conn.cursor()
    except sqlite3.OperationalError:
        print("\n❌ Error: Database not found!")
        print("   Run 'python scraper.py' first to create the database")
        return
    
    print("\n" + "=" * 70)
    print(" " * 20 + "HP-PULSE SCRAPER DASHBOARD")
    print(" " * 25 + f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # ============================================
    # OVERALL STATISTICS
    # ============================================
    print("\n📊 OVERALL STATISTICS")
    print("─" * 70)
    
    total_companies = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    total_leads = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_scrapes = c.execute("SELECT COUNT(*) FROM scrape_log").fetchone()[0]
    
    print(f"   Total Companies:     {total_companies:,}")
    print(f"   Total Leads:         {total_leads:,}")
    print(f"   Total Scrape Runs:   {total_scrapes:,}")
    
    # Today's stats
    today = datetime.now().date().isoformat()
    today_leads = c.execute(
        "SELECT COUNT(*) FROM leads WHERE DATE(scraped_at) = ?", 
        (today,)
    ).fetchone()[0]
    today_scrapes = c.execute(
        "SELECT COUNT(*) FROM scrape_log WHERE DATE(scraped_at) = ?",
        (today,)
    ).fetchone()[0]
    
    print(f"\n   📅 Today's Activity:")
    print(f"      Leads Found:      {today_leads:,}")
    print(f"      Scrape Runs:      {today_scrapes:,}")
    
    # ============================================
    # LEADS BY TYPE
    # ============================================
    print("\n📈 LEADS BY TYPE")
    print("─" * 70)
    
    lead_types = c.execute("""
        SELECT signal_type, COUNT(*) as count
        FROM leads
        GROUP BY signal_type
        ORDER BY count DESC
    """).fetchall()
    
    if lead_types:
        for signal_type, count in lead_types:
            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"   {signal_type.capitalize():15} {count:4,} │ {bar} {percentage:.1f}%")
    else:
        print("   No leads found yet")
    
    # ============================================
    # TOP COMPANIES
    # ============================================
    print("\n🏢 TOP COMPANIES (By Lead Volume)")
    print("─" * 70)
    
    top_companies = c.execute("""
        SELECT c.name, COUNT(l.id) as lead_count
        FROM companies c
        JOIN leads l ON c.id = l.company_id
        GROUP BY c.name
        ORDER BY lead_count DESC
        LIMIT 10
    """).fetchall()
    
    if top_companies:
        for i, (company, count) in enumerate(top_companies, 1):
            print(f"   {i:2}. {company[:50]:50} {count:3} leads")
    else:
        print("   No company data yet")
    
    # ============================================
    # RECENT SCRAPE ACTIVITY
    # ============================================
    print("\n⏰ RECENT SCRAPE ACTIVITY")
    print("─" * 70)
    
    recent_scrapes = c.execute("""
        SELECT source_name, scraped_at, status, items_found
        FROM scrape_log
        ORDER BY scraped_at DESC
        LIMIT 15
    """).fetchall()
    
    if recent_scrapes:
        table_data = []
        for source, timestamp, status, items in recent_scrapes:
            # Format timestamp
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%m-%d %H:%M")
            
            # Status emoji
            status_emoji = "✅" if status == "success" else "❌"
            
            # Truncate source name
            source_short = source[:35]
            
            table_data.append([source_short, time_str, f"{status_emoji} {status[:10]}", items])
        
        print(tabulate(table_data, 
                       headers=["Source", "Time", "Status", "Items"],
                       tablefmt="simple"))
    else:
        print("   No scrape activity yet")
    
    # ============================================
    # SUCCESS RATE
    # ============================================
    print("\n✅ SUCCESS RATE")
    print("─" * 70)
    
    # Last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    stats_24h = c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes
        FROM scrape_log
        WHERE scraped_at > ?
    """, (yesterday,)).fetchone()
    
    if stats_24h[0] > 0:
        success_rate_24h = (stats_24h[1] / stats_24h[0]) * 100
        print(f"   Last 24 hours: {success_rate_24h:.1f}% ({stats_24h[1]}/{stats_24h[0]} successful)")
    else:
        print("   Last 24 hours: No scrapes yet")
    
    # Overall
    stats_all = c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes
        FROM scrape_log
    """).fetchone()
    
    if stats_all[0] > 0:
        success_rate_all = (stats_all[1] / stats_all[0]) * 100
        print(f"   Overall:       {success_rate_all:.1f}% ({stats_all[1]}/{stats_all[0]} successful)")
    
    # ============================================
    # RECENT LEADS
    # ============================================
    print("\n🎯 RECENT HIGH-CONFIDENCE LEADS")
    print("─" * 70)
    
    recent_leads = c.execute("""
        SELECT c.name, l.signal_type, l.confidence, l.scraped_at
        FROM leads l
        JOIN companies c ON l.company_id = c.id
        WHERE l.confidence >= 0.7
        ORDER BY l.scraped_at DESC
        LIMIT 10
    """).fetchall()
    
    if recent_leads:
        table_data = []
        for company, sig_type, confidence, timestamp in recent_leads:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%m-%d %H:%M")
            conf_pct = f"{confidence*100:.0f}%"
            
            table_data.append([company[:40], sig_type, conf_pct, time_str])
        
        print(tabulate(table_data,
                       headers=["Company", "Type", "Confidence", "Time"],
                       tablefmt="simple"))
    else:
        print("   No high-confidence leads yet")
    
    # ============================================
    # FOOTER
    # ============================================
    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("   • Run 'python scraper.py' to start/resume scraping")
    print("   • Check 'hp_pulse.db' with SQLite for detailed queries")
    print("   • Press Ctrl+C in scraper window to stop")
    print("=" * 70)
    print()
    
    conn.close()

def show_quick_stats():
    """Show quick one-line stats"""
    try:
        conn = sqlite3.connect('hp_pulse.db')
        c = conn.cursor()
        
        total_companies = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        total_leads = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        
        today = datetime.now().date().isoformat()
        today_leads = c.execute(
            "SELECT COUNT(*) FROM leads WHERE DATE(scraped_at) = ?", 
            (today,)
        ).fetchone()[0]
        
        print(f"HP-Pulse: {total_companies} companies, {total_leads} leads ({today_leads} today)")
        
        conn.close()
    except:
        print("HP-Pulse: Database not initialized")

def export_to_csv(filename='leads_export.csv'):
    """Export leads to CSV file"""
    import csv
    
    try:
        conn = sqlite3.connect('hp_pulse.db')
        c = conn.cursor()
        
        # Get all leads with company information
        leads = c.execute("""
            SELECT 
                l.id,
                c.name as company_name,
                c.industry,
                c.location,
                l.signal_type,
                l.signal_text,
                l.source_name,
                l.source_url,
                l.confidence,
                l.scraped_at
            FROM leads l
            JOIN companies c ON l.company_id = c.id
            ORDER BY l.scraped_at DESC
        """).fetchall()
        
        if not leads:
            print("No leads to export")
            conn.close()
            return
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Company', 'Industry', 'Location', 'Signal Type', 
                           'Signal Text', 'Source', 'Source URL', 'Confidence', 'Scraped At'])
            writer.writerows(leads)
        
        print(f"\n✅ Exported {len(leads)} leads to {filename}")
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            show_quick_stats()
        elif sys.argv[1] == "--export":
            filename = sys.argv[2] if len(sys.argv) > 2 else 'leads_export.csv'
            export_to_csv(filename)
        else:
            show_dashboard()
    else:
        show_dashboard()

