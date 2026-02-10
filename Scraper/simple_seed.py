"""
Simple seed script using direct SQLite connection
"""
import sqlite3
import json
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('/Users/abhinavbajpai/Documents/Hackathon/IITR-HPCL-3/IITR-HPCL/Scraper/hp_pulse.db')
c = conn.cursor()

COMPANY_NAMES = [
    "Reliance Industries", "Adani Enterprises", "Tata Steel", "JSW Steel", "Vedanta Ltd",
    "Dalmia Bharat", "UltraTech Cement", "Asian Paints", "Pidilite Industries",
    "Grasim Industries", "Ambuja Cements", "Shree Cement", "Hindalco", "Larsen & Toubro",
    "NTPC", "BHEL", "NHPC", "Power Grid", "Coal India",
    "Wipro Data Center", "Apollo Hospitals", "Max Healthcare", "Marriott Hotels",
    "Taj Group", "Hyatt Regency", "DLF Infrastructure", "Lodha Group", "Godrej Properties"
]

INDUSTRIES = [
    "Steel & Metal", "Cement", "Chemical", "Paper & Pulp", "Sugar",
    "Fertilizer", "Pharmaceutical", "Glass", "Ceramic", "Textile", "Power",
    "Hospitality", "Healthcare", "Infrastructure", "Real Estate"
]

PRODUCTS = ["HSD", "FO", "BITUMEN", "LDO", "BUNKER", "JBO"]
LOCATIONS = ["Mumbai", "Delhi", "Pune", "Chennai", "Bangalore", "Hyderabad", "Kolkata"]
SIGNAL_TYPES = ["TENDER", "NEWS", "DIRECTORY"]
SOURCES = {
    "TENDER": ["GeM Portal", "CPPP Portal"],
    "NEWS": ["Financial Express", "Economic Times", "Business Standard"],
    "DIRECTORY": ["Company Website", "LinkedIn"]
}

# Clear existing data
print("Clearing existing data...")
c.execute("DELETE FROM leads")
c.execute("DELETE FROM companies")
conn.commit()
print("✅ Cleared")

print("\nCreating companies and leads...")
base_date = datetime.now() - timedelta(days=30)
company_ids = {}
created = 0

for i in range(100):
    company_idx = i % len(COMPANY_NAMES)
    industry_idx = (i + 2) % len(INDUSTRIES)
    product_idx = (i + 5) % len(PRODUCTS)
    location_idx = (i + 3) % len(LOCATIONS)
    
    company_name = COMPANY_NAMES[company_idx]
    industry = INDUSTRIES[industry_idx]
    product = PRODUCTS[product_idx]
    location = LOCATIONS[location_idx]
    
    # Create or get company
    if company_name not in company_ids:
        normalized = company_name.lower().strip()
        c.execute("SELECT id FROM companies WHERE normalized_name = ?", (normalized,))
        existing = c.fetchone()
        
        if existing:
            company_id = existing[0]
        else:
            c.execute('''INSERT INTO companies (name, normalized_name, industry, location, created_at)
                        VALUES (?, ?, ?, ?, ?)''',
                     (company_name, normalized, industry, location, datetime.now().isoformat()))
            company_id = c.lastrowid
        
        company_ids[company_name] = company_id
    else:
        company_id = company_ids[company_name]
    
    # Signal properties
    rand_val = (i * 7) % 100
    if rand_val < 20:
        signal_type = "TENDER"
    elif rand_val < 90:
        signal_type =  "NEWS"
    else:
        signal_type = "DIRECTORY"
    
    source = random.choice(SOURCES[signal_type])
    has_volume = (i % 4) == 0
    has_capacity = (i % 2) == 0
    
    # Confidence
    confidence = 0.70
    if signal_type == "TENDER":
        confidence = 0.85
    if has_volume:
        confidence += 0.10
    if has_capacity:
        confidence += 0.05
    confidence = min(0.98, confidence + random.uniform(-0.05, 0.05))
    
    # Status
    if confidence >= 0.90:
        status = "AUTO_ASSIGNED"
    elif confidence >= 0.75:
        status = "QUALIFIED"
    else:
        status = "REVIEW_REQUIRED"
    
    # Signal text
    signal_text = f"{company_name} showing interest in {product}"
    if has_volume:
        signal_text += f". Volume: {random.randint(100, 5000)} MT/month"
    if has_capacity:
        signal_text += f". Capacity expansion at {location}"
    
    timestamp = (base_date + timedelta(days=i % 30, hours=i % 24)).isoformat()
    products_json = json.dumps([product])
    
    c.execute('''INSERT INTO leads 
                (company_id, signal_text, signal_type, source_name, source_url,
                 products_mentioned, confidence, scraped_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
             (company_id, signal_text, signal_type, source,
              f"https://example.com/{i}", products_json, 
              round(confidence, 2), timestamp, status))
    created += 1
    
    if created % 25 == 0:
        print(f"  Created {created} leads...")

conn.commit()

#Stats
print(f"\n✅ Created {len(company_ids)} companies and {created} leads\n")

print("📈 Stats:")
c.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n📊 By Type:")
c.execute("SELECT signal_type, COUNT(*) FROM leads GROUP BY signal_type")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

c.execute("SELECT COUNT(*) FROM leads WHERE confidence >= 0.90")
print(f"\n⭐ High Confidence: {c.fetchone()[0]}")

conn.close()
print("\n✅ Done!")
