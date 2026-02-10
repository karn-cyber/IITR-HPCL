"""
Database operations for HP-Pulse Scraper
"""

import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path='hp_pulse.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Companies table
        c.execute('''CREATE TABLE IF NOT EXISTS companies
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      normalized_name TEXT,
                      industry TEXT,
                      location TEXT,
                      website TEXT,
                      created_at TEXT)''')
        
        # Leads table
        c.execute('''CREATE TABLE IF NOT EXISTS leads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      company_id INTEGER,
                      signal_text TEXT,
                      signal_type TEXT,
                      source_name TEXT,
                      source_url TEXT,
                      products_mentioned TEXT,
                      confidence REAL,
                      scraped_at TEXT,
                      processed BOOLEAN DEFAULT 0,
                      FOREIGN KEY (company_id) REFERENCES companies (id))''')
        
        # Scrape log table
        c.execute('''CREATE TABLE IF NOT EXISTS scrape_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      source_name TEXT,
                      source_type TEXT,
                      status TEXT,
                      items_found INTEGER,
                      error_message TEXT,
                      scraped_at TEXT)''')
        
        # Source registry
        c.execute('''CREATE TABLE IF NOT EXISTS source_registry
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      domain TEXT UNIQUE,
                      category TEXT,
                      trust_score INTEGER,
                      robots_compliant BOOLEAN,
                      last_checked TEXT)''')
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_leads_scraped_at ON leads(scraped_at)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_leads_company_id ON leads(company_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_companies_normalized ON companies(normalized_name)')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def insert_company(self, name, industry=None, location=None, website=None):
        """Insert or get company"""
        conn = self.get_connection()
        c = conn.cursor()
        
        normalized = name.lower().strip()
        
        # Check if exists
        c.execute("SELECT id FROM companies WHERE normalized_name = ?", (normalized,))
        existing = c.fetchone()
        
        if existing:
            company_id = existing[0]
        else:
            c.execute('''INSERT INTO companies 
                         (name, normalized_name, industry, location, website, created_at)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (name, normalized, industry, location, website, 
                       datetime.now().isoformat()))
            company_id = c.lastrowid
        
        conn.commit()
        conn.close()
        return company_id
    
    def insert_lead(self, company_id, signal_text, signal_type, source_name, 
                    source_url, products=None, confidence=0.0):
        """Insert a new lead"""
        conn = self.get_connection()
        c = conn.cursor()
        
        products_json = json.dumps(products) if products else None
        
        c.execute('''INSERT INTO leads 
                     (company_id, signal_text, signal_type, source_name, 
                      source_url, products_mentioned, confidence, scraped_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (company_id, signal_text, signal_type, source_name, 
                   source_url, products_json, confidence, datetime.now().isoformat()))
        
        lead_id = c.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    
    def log_scrape(self, source_name, source_type, status, items_found, error=None):
        """Log scraping attempt"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO scrape_log 
                     (source_name, source_type, status, items_found, 
                      error_message, scraped_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (source_name, source_type, status, items_found, 
                   error, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_recent_leads(self, limit=10):
        """Get recent leads"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT l.id, c.name, l.signal_text, l.signal_type, 
                            l.source_name, l.confidence, l.scraped_at
                     FROM leads l
                     JOIN companies c ON l.company_id = c.id
                     ORDER BY l.scraped_at DESC
                     LIMIT ?''', (limit,))
        
        results = c.fetchall()
        conn.close()
        return results
    
    def get_stats(self):
        """Get database statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        
        stats = {}
        
        # Total counts
        stats['total_companies'] = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        stats['total_leads'] = c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        
        # Today's leads
        today = datetime.now().date().isoformat()
        stats['today_leads'] = c.execute(
            "SELECT COUNT(*) FROM leads WHERE DATE(scraped_at) = ?", 
            (today,)
        ).fetchone()[0]
        
        # Leads by type
        stats['by_type'] = c.execute("""
            SELECT signal_type, COUNT(*) as count
            FROM leads
            GROUP BY signal_type
            ORDER BY count DESC
        """).fetchall()
        
        conn.close()
        return stats
