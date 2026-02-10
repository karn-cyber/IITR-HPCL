"""
Extended database module for the backend API
Extends the existing SQLite database with new tables for the API
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import json
import sys
from typing import Optional, List, Dict, Any
from ..config import settings

# Import the base database class to initialize base schema
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from utils.database import Database as BaseDatabase


class DatabaseExtended:
    """Extended database operations for the API"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        # Initialize base schema first
        self._init_base_schema()
        # Then add extended schema
        self.init_extended_schema()
    
    def _init_base_schema(self):
        """Initialize base database schema using the original Database class"""
        try:
            base_db = BaseDatabase(self.db_path)
            print("✅ Base database schema initialized")
        except Exception as e:
            print(f"⚠️  Base schema initialization: {e}")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_extended_schema(self):
        """Initialize extended schema for API features"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            territory TEXT,
            territory_id INTEGER,
            alert_preferences TEXT,
            email_enabled BOOLEAN DEFAULT 1,
            push_enabled BOOLEAN DEFAULT 0,
            min_confidence REAL DEFAULT 0.7,
            products TEXT,
            territories TEXT,
            active BOOLEAN DEFAULT 1,
            last_login TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (territory_id) REFERENCES territories (id)
        )''')
        
        # Lead actions table
        c.execute('''CREATE TABLE IF NOT EXISTS lead_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            notes TEXT,
            next_follow_up TEXT,
            estimated_deal_value REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Lead notes table
        c.execute('''CREATE TABLE IF NOT EXISTS lead_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Lead documents table
        c.execute('''CREATE TABLE IF NOT EXISTS lead_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Products table
        c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            base_confidence_rules TEXT,
            primary_keywords TEXT,
            secondary_keywords TEXT,
            negative_keywords TEXT,
            scoring_factors TEXT,
            disqualifiers TEXT,
            updated_at TEXT NOT NULL,
            updated_by INTEGER,
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )''')
        
        # Territories table
        c.execute('''CREATE TABLE IF NOT EXISTS territories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            depot TEXT,
            coverage_areas TEXT,
            depot_lat REAL,
            depot_lng REAL,
            assigned_officers TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )''')
        
        # Feedback table
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            reason TEXT,
            correct_product TEXT,
            correct_industry TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Audit log table
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT NOT NULL,
            resource_id TEXT,
            changes TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        
        # Extend leads table with new columns (add if not exists)
        try:
            c.execute('ALTER TABLE leads ADD COLUMN status TEXT DEFAULT "REVIEW_REQUIRED"')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            c.execute('ALTER TABLE leads ADD COLUMN assigned_to TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE leads ADD COLUMN territory TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE leads ADD COLUMN scoring TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE leads ADD COLUMN estimated_value REAL')
        except sqlite3.OperationalError:
            pass
        
        # Extend companies table
        try:
            c.execute('ALTER TABLE companies ADD COLUMN lat REAL')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE companies ADD COLUMN lng REAL')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE companies ADD COLUMN existing_customer BOOLEAN DEFAULT 0')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE companies ADD COLUMN hpcl_customer_id TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            c.execute('ALTER TABLE companies ADD COLUMN history TEXT')
        except sqlite3.OperationalError:
            pass
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_lead_actions_lead_id ON lead_actions(lead_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_lead_notes_lead_id ON lead_notes(lead_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_territories_name ON territories(name)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_feedback_lead_id ON feedback(lead_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_leads_assigned_to ON leads(assigned_to)')
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, email: str, password_hash: str, name: str, role: str, territory: str = None) -> int:
        """Create a new user"""
        conn = self.get_connection()
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        c.execute('''INSERT INTO users 
                     (email, password_hash, name, role, territory, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (email, password_hash, name, role, territory, now, now))
        
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_user_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('UPDATE users SET last_login = ? WHERE id = ?',
                  (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    # Lead operations
    def get_leads_paginated(self, page: int = 1, limit: int = 50, 
                           filter_status: str = None, 
                           search: str = None,
                           min_confidence: float = None,
                           product_code: str = None,
                           location: str = None,
                           sort_by: str = 'confidence',
                           sort_order: str = 'desc') -> Dict[str, Any]:
        """Get paginated leads with filters"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Build query
        where_clauses = []
        params = []
        
        if filter_status and filter_status != 'ALL':
            where_clauses.append('l.status = ?')
            params.append(filter_status)
        
        if search:
            where_clauses.append('(c.name LIKE ? OR l.signal_text LIKE ?)')
            search_term = f'%{search}%'
            params.extend([search_term, search_term])
        
        if min_confidence is not None:
            where_clauses.append('l.confidence >= ?')
            params.append(min_confidence)
        
        if product_code:
            where_clauses.append('l.products_mentioned LIKE ?')
            params.append(f'%{product_code}%')
        
        if location:
            where_clauses.append('c.location LIKE ?')
            params.append(f'%{location}%')
        
        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
        
        # Get total count
        count_query = f'''
            SELECT COUNT(*) as total
            FROM leads l
            JOIN companies c ON l.company_id = c.id
            WHERE {where_sql}
        '''
        c.execute(count_query, params)
        total = c.fetchone()['total']
        
        # Get paginated results
        offset = (page - 1) * limit
        order_column = {
            'confidence': 'l.confidence',
            'timestamp': 'l.scraped_at',
            'company': 'c.name',
            'status': 'l.status',
            'signal_type': 'l.signal_type',
            'source': 'l.source_name'
        }.get(sort_by, 'l.confidence')
        
        order_dir = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        
        query = f'''
            SELECT l.*, c.name as company_name, c.industry, c.location
            FROM leads l
            JOIN companies c ON l.company_id = c.id
            WHERE {where_sql}
            ORDER BY {order_column} {order_dir}
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        leads = [dict(row) for row in rows]
        
        return {
            'leads': leads,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'totalPages': (total + limit - 1) // limit
            }
        }
    
    def get_lead_by_id(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed lead information"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Get lead with company info
        c.execute('''
            SELECT l.*, c.name as company_name, c.industry, c.location,
                   c.lat, c.lng, c.existing_customer, c.hpcl_customer_id, c.history
            FROM leads l
            JOIN companies c ON l.company_id = c.id
            WHERE l.id = ?
        ''', (lead_id,))
        
        row = c.fetchone()
        if not row:
            conn.close()
            return None
        
        lead = dict(row)
        
        # Get actions
        c.execute('''
            SELECT la.*, u.name as user_name
            FROM lead_actions la
            JOIN users u ON la.user_id = u.id
            WHERE la.lead_id = ?
            ORDER BY la.created_at DESC
        ''', (lead_id,))
        lead['actions'] = [dict(r) for r in c.fetchall()]
        
        # Get notes
        c.execute('''
            SELECT ln.*, u.name as user_name
            FROM lead_notes ln
            JOIN users u ON ln.user_id = u.id
            WHERE ln.lead_id = ?
            ORDER BY ln.created_at DESC
        ''', (lead_id,))
        lead['notes'] = [dict(r) for r in c.fetchall()]
        
        # Get documents
        c.execute('''
            SELECT ld.*, u.name as user_name
            FROM lead_documents ld
            JOIN users u ON ld.user_id = u.id
            WHERE ld.lead_id = ?
            ORDER BY ld.uploaded_at DESC
        ''', (lead_id,))
        lead['documents'] = [dict(r) for r in c.fetchall()]
        
        conn.close()
        return lead
    
    def add_lead_action(self, lead_id: int, user_id: int, action_type: str,
                       notes: str = None, next_follow_up: str = None,
                       estimated_deal_value: float = None) -> int:
        """Add an action to a lead"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO lead_actions
                     (lead_id, user_id, action_type, notes, next_follow_up, 
                      estimated_deal_value, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (lead_id, user_id, action_type, notes, next_follow_up,
                   estimated_deal_value, datetime.now().isoformat()))
        
        action_id = c.lastrowid
        
        # Update lead status based on action
        status_map = {
            'ACCEPT': 'ACCEPTED',
            'REJECT': 'REJECTED',
            'CONVERT': 'CONVERTED'
        }
        
        if action_type in status_map:
            c.execute('UPDATE leads SET status = ? WHERE id = ?',
                     (status_map[action_type], lead_id))
        
        conn.commit()
        conn.close()
        return action_id
    
    def add_lead_note(self, lead_id: int, user_id: int, note: str) -> int:
        """Add a note to a lead"""
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO lead_notes (lead_id, user_id, note, created_at)
                     VALUES (?, ?, ?, ?)''',
                  (lead_id, user_id, note, datetime.now().isoformat()))
        
        note_id = c.lastrowid
        conn.commit()
        conn.close()
        return note_id


# Singleton instance
db = DatabaseExtended()
