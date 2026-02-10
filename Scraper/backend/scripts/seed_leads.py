"""
Seed realistic lead data into the database
Based on the frontend mock data structure
"""
import sys
from pathlib import Path
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.models.database import db
import json

COMPANY_NAMES = [
    "Reliance Industries", "Adani Enterprises", "Tata Steel", "JSW Steel", "Vedanta Ltd",
    "Dalmia Bharat", "UltraTech Cement", "Asian Paints", "Pidilite Industries", "Coromandel International",
    "Grasim Industries", "Ambuja Cements", "Shree Cement", "Hindalco", "Larsen & Toubro",
    "NTPC", "BHEL", "NHPC", "Power Grid", "Coal India", "ONGC", "IOCL", "BPCL",
    "Infosys Data Center", "Wipro Cloud", "Apollo Hospitals", "Max Healthcare", "Marriott Hotels",
    "Taj Group", "Hyatt Regency", "DLF Infrastructure", "Lodha Group", "Godrej Properties",
    "ITC Limited", "Hindustan Unilever", "Sun Pharma", "Dr. Reddy's Labs", "Cipla",
    "Torrent Power", "Adani Power", "Essar Steel", "Jindal Steel", "Vedanta Aluminum"
]

INDUSTRIES = [
    "Steel & Metal", "Cement", "Chemical", "Paper & Pulp", "Sugar", "Distillery",
    "Fertilizer", "Pharmaceutical", "Glass", "Ceramic", "Textile", "Rubber", "Power",
    "Hospitality", "Healthcare", "Infrastructure", "IT Services", "Real Estate"
]

PRODUCT_CODES = ["HSD", "LDO", "FO", "BITUMEN", "BUNKER", "HEXANE", "PROPYLENE", "JBO", 
                 "SOLVENT_1425", "MTO_2445", "SULPHUR", "SKO_NON_PDS"]

LOCATIONS = ["Mumbai", "Ahmedabad", "Pune", "Chennai", "Kolkata", "Delhi", "Bangalore", 
             "Hyderabad", "Visakhapatnam", "Jaipur", "Lucknow", "Indore"]

SIGNAL_TYPES = ["TENDER", "NEWS", "DIRECTORY"]

SOURCES = {
    "TENDER": ["GeM Portal", "CPPP Portal", "State Tender Board"],
    "NEWS": ["Financial Express", "Economic Times", "Business Standard", "Mint"],
    "DIRECTORY": ["Company Website", "LinkedIn", "IndiaMART", "TradeIndia"]
}

def calculate_confidence(signal_type, has_volume, has_capacity):
    """Calculate confidence score based on signal properties"""
    base = 0.65
    if signal_type == "TENDER":
        base = 0.85
    elif signal_type == "NEWS":
        base = 0.70
    
    if has_volume:
        base += 0.10
    if has_capacity:
        base += 0.08
        
    # Add some randomness
    base += random.uniform(-0.05, 0.05)
    
    return min(0.98, max(0.50, base))

def get_reason_codes(confidence, signal_type, has_volume, has_capacity):
    """Generate reason codes based on signal properties"""
    codes = []
    
    if signal_type == "TENDER":
        codes.append("EXPLICIT_TENDER")
    if has_volume:
        codes.append("VOLUME_MENTIONED")
    if has_capacity:
        codes.append("CAPACITY_EXPANSION")
    if confidence > 0.85:
        codes.append("HIGH_CONFIDENCE_INDUSTRY")
    if random.random() > 0.7:
        codes.append("PROXIMITY_TO_DEPOT")
        
    return codes

def get_status(confidence):
    """Determine lead status based on confidence"""
    if confidence >= 0.90:
        return "AUTO_ASSIGNED"
    elif confidence >= 0.75:
        return "QUALIFIED"
    else:
        return "REVIEW_REQUIRED"

def clear_existing_leads():
    """Clear all existing leads and companies from database"""
    print("🗑️  Clearing existing leads and companies...")
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM leads")
    c.execute("DELETE FROM companies")
    conn.commit()
    conn.close()
    print("✅ Cleared existing data")

def seed_leads(count=100):
    """Seed realistic lead data"""
    print(f"\n🌱 Seeding {count} quality leads...")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # Get existing users for assignment
    c.execute("SELECT id, role FROM users WHERE role IN ('SALES_OFFICER', 'MANAGER')")
    users = c.fetchall()
    
    created_leads = 0
    created_companies = 0
    base_date = datetime.now() - timedelta(days=30)
    
    # Track created companies to avoid duplicates
    company_ids = {}
    
    for i in range(count):
        # Generate predictable but varied data
        company_idx = i % len(COMPANY_NAMES)
        industry_idx = (i + 2) % len(INDUSTRIES)
        product_idx = (i + 5) % len(PRODUCT_CODES)
        location_idx = (i + 3) % len(LOCATIONS)
        
        company_name = COMPANY_NAMES[company_idx]
        industry = INDUSTRIES[industry_idx]
        product = PRODUCT_CODES[product_idx]
        location = LOCATIONS[location_idx]
        
        # Create or get company
        if company_name not in company_ids:
            normalized_name = company_name.lower().strip()
            c.execute("SELECT id FROM companies WHERE normalized_name = ?", (normalized_name,))
            existing = c.fetchone()
            
            if existing:
                company_id = existing[0]
            else:
                c.execute('''INSERT INTO companies 
                            (name, normalized_name, industry, location, created_at)
                            VALUES (?, ?, ?, ?, ?)''',
                         (company_name, normalized_name, industry, location, 
                          datetime.now().isoformat()))
                company_id = c.lastrowid
                created_companies += 1
            
            company_ids[company_name] = company_id
        else:
            company_id = company_ids[company_name]
        
        # Determine signal type (70% NEWS, 20% TENDER, 10% DIRECTORY)
        rand_val = (i * 7) % 100
        if rand_val < 20:
            signal_type = "TENDER"
        elif rand_val < 90:
            signal_type = "NEWS"
        else:
            signal_type = "DIRECTORY"
        
        source_name = random.choice(SOURCES[signal_type])
        
        # Signal properties
        has_volume = (i % 4) == 0
        has_capacity = (i % 2) == 0
        
        # Calculate confidence and derived fields
        confidence = calculate_confidence(signal_type, has_volume, has_capacity)
        reason_codes = get_reason_codes(confidence, signal_type, has_volume, has_capacity)
        status = get_status(confidence)
        
        # Assign to user for high confidence leads
        assigned_to = None
        if status == "AUTO_ASSIGNED" and users:
            assigned_to = random.choice(users)[0]
        
        # Generate timestamp (spread over last 30 days)
        timestamp = (base_date + timedelta(days=i % 30, hours=i % 24)).isoformat()
        
        # Create signal description
        signal_text = f"{company_name} {signal_type.lower()} indicating strong interest in {product}"
        if has_volume:
            signal_text += f". Volume requirements mentioned: {random.randint(100, 5000)} MT/month"
        if has_capacity:
            signal_text += f". Planning capacity expansion at {location} facility"
            
        # Products mentioned
        products_mentioned = json.dumps([product])
        
        try:
            c.execute('''INSERT INTO leads 
                        (company_id, signal_text, signal_type, source_name, source_url,
                         products_mentioned, confidence, scraped_at, status, assigned_to)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (company_id, signal_text, signal_type, source_name,
                      f"https://example.com/{signal_type.lower()}/{i}",
                      products_mentioned, round(confidence, 2), timestamp, 
                      status, assigned_to))
            created_leads += 1
            
            if (created_leads) % 25 == 0:
                print(f"  📊 Created {created_leads} leads...")
                
        except Exception as e:
            print(f"  ⚠️  Error creating lead {i}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully created {created_companies} companies and {created_leads} leads")
    
    # Print stats
    conn = db.get_connection()
    c = conn.cursor()
    
    print("\n📈 Lead Statistics:")
    c.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    for status, count in c.fetchall():
        print(f"  {status}: {count}")
    
    c.execute("SELECT signal_type, COUNT(*) FROM leads GROUP BY signal_type")
    print("\n📊 By Signal Type:")
    for sig_type, count in c.fetchall():
        print(f"  {sig_type}: {count}")
        
    c.execute("SELECT COUNT(*) FROM leads WHERE confidence >= 0.90")
    high_conf = c.fetchone()[0]
    print(f"\n⭐ High Confidence (≥90%): {high_conf}")
    
    c.execute("SELECT COUNT(DISTINCT company_id) FROM leads")
    unique_companies = c.fetchone()[0]
    print(f"🏢 Unique Companies: {unique_companies}")
    
    conn.close()


def main():
    """Run the seeding process"""
    print("=" * 70)
    print("🌱 HPCL Lead Intelligence - Lead Data Seeding")
    print("=" * 70)
    
    response = input("\n⚠️  This will CLEAR all existing leads. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Seeding cancelled")
        return
    
    clear_existing_leads()
    seed_leads(100)  # Create 100 quality leads
    
    print("\n" + "=" * 70)
    print("✅ Lead seeding completed successfully!")
    print("=" * 70)
    print("\n💡 Refresh the frontend to see the new data")
    print("")


if __name__ == '__main__':
    main()
