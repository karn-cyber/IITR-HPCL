"""
Seed Test Data
Inserts a high-quality test lead to verify Intelligence Services in the Dashboard.
"""

import sys
import os
sys.path.append(os.path.abspath("Scraper"))

from backend.app.models.database import DatabaseExtended as Database
from utils.compliance import ComplianceChecker
from scrapers.tender_scraper import TenderScraper

def seed_data():
    print("🚀 Seeding Test Data...")
    
    # Init
    db = Database()
    checker = ComplianceChecker()
    scraper = TenderScraper(db, checker)
    
    # Create Test User for Notifications
    print("👤 Creating Test User with WhatsApp enabled...")
    try:
        # Check if exists
        user = db.get_user_by_email("test@hpcl.in")
        if not user:
            uid = db.create_user(
                email="test@hpcl.in",
                password_hash="hashed_secret",
                name="Test Officer",
                role="officer",
                territory="Mumbai"
            )
            # Enable WhatsApp
            conn = db.get_connection()
            c = conn.cursor()
            import json
            prefs = json.dumps({"whatsapp_enabled": True, "phone": "919876543210"})
            c.execute("UPDATE users SET alert_preferences = ? WHERE id = ?", (prefs, uid))
            conn.commit()
            conn.close()
            print("   ✅ Test User Created")
        else:
            print("   ℹ️ Test User already exists")
    except Exception as e:
        print(f"   ⚠️ Could not create test user: {e}")
    
    # Test Signal
    test_text = """
    NOTICE INVITING TENDER: Supply of 5000 KL of Furnace Oil (FO) and 
    200 MT of Bitumen (VG-30) for the new Mumbai-Pune Expressway expansion project.
    Estimated value: 50 Crore. Urgent requirement for heating and paving application.
    """
    
    print(f"\n📝 Processing Test Signal:\n{test_text.strip()}\n")
    
    # Process
    lead_id, products = scraper.process_lead(
        company_name="MSRDC Infrastructure Ltd.",
        signal_text=test_text,
        source_name="Manual Test Injection",
        source_url="http://test-injection.local",
        signal_type="tender"
    )
    
    print(f"✅ Lead Inserted! ID: {lead_id}")
    print("\n🔍 Verification Points for Dashboard:")
    print("1. Company Name: 'msrdc infrastructure' (Normalized)")
    print(f"2. Products: {[p['name'] for p in products]} (Inferred)")
    print("3. Score: Should be High (> 0.8) due to 'Tender', '5000 KL', 'Crore'")
    print("4. Notification: Check console logs for WhatsApp alert attempt")

if __name__ == "__main__":
    seed_data()
