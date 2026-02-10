"""
Database seeding script
Creates initial users, products, and territories
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.models.database import db
from backend.app.utils.security import get_password_hash
import json
from datetime import datetime


def seed_users():
    """Create initial users"""
    print("Seeding users...")
    
    users = [
        {
            'email': 'admin@hpcl.com',
            'password': 'admin123',
            'name': 'Admin User',
            'role': 'ADMIN',
            'territory': None
        },
        {
            'email': 'officer@hpcl.com',
            'password': 'officer123',
            'name': 'Regional Sales Officer',
            'role': 'SALES_OFFICER',
            'territory': 'Mumbai West'
        },
        {
            'email': 'manager@hpcl.com',
            'password': 'manager123',
            'name': 'Sales Manager',
            'role': 'MANAGER',
            'territory': 'West Zone'
        }
    ]
    
    for user_data in users:
        existing = db.get_user_by_email(user_data['email'])
        if not existing:
            password_hash = get_password_hash(user_data['password'])
            user_id = db.create_user(
                email=user_data['email'],
                password_hash=password_hash,
                name=user_data['name'],
                role=user_data['role'],
                territory=user_data['territory']
            )
            print(f"✅ Created user: {user_data['email']} (ID: {user_id})")
        else:
            print(f"⏭️  User already exists: {user_data['email']}")


def seed_products():
    """Create initial products"""
    print("\nSeeding products...")
    
    conn = db.get_connection()
    c = conn.cursor()
    
    products = [
        {
            'code': 'HSD',
            'name': 'High Speed Diesel',
            'category': 'Fuels',
            'base_confidence_rules': json.dumps({
                'explicitTenderWithVolume': 0.95,
                'gensetInstallationAnnouncement': 0.85,
                'dieselMention': 0.70
            }),
            'primary_keywords': json.dumps([
                'high speed diesel', 'HSD', 'diesel', 'diesel genset', 'genset fuel'
            ]),
            'secondary_keywords': json.dumps([
                'power backup', 'generator', 'captive power', 'DG set'
            ]),
            'negative_keywords': json.dumps([
                'retail', 'petrol pump', 'filling station'
            ])
        },
        {
            'code': 'FO',
            'name': 'Furnace Oil',
            'category': 'Fuels',
            'base_confidence_rules': json.dumps({
                'explicitTenderWithVolume': 0.95,
                'furnaceInstallation': 0.85,
                'boilerMention': 0.75
            }),
            'primary_keywords': json.dumps([
                'furnace oil', 'FO', 'LSHS', 'fuel oil'
            ]),
            'secondary_keywords': json.dumps([
                'boiler', 'furnace', 'industrial heating', 'thermal power'
            ]),
            'negative_keywords': json.dumps([
                'automotive', 'vehicle'
            ])
        },
        {
            'code': 'BITUMEN',
            'name': 'Bitumen',
            'category': 'Specialty',
            'base_confidence_rules': json.dumps({
                'roadConstructionTender': 0.92,
                'bitumenMention': 0.80
            }),
            'primary_keywords': json.dumps([
                'bitumen', 'asphalt', 'road construction', 'highway project'
            ]),
            'secondary_keywords': json.dumps([
                'paving', 'surfacing', 'road work', 'NHAI'
            ]),
            'negative_keywords': json.dumps([])
        },
        {
            'code': 'MS',
            'name': 'Motor Spirit (Petrol)',
            'category': 'Fuels',
            'base_confidence_rules': json.dumps({
                'explicitTender': 0.90,
                'fleetRequirement': 0.75
            }),
            'primary_keywords': json.dumps([
                'motor spirit', 'MS', 'petrol', 'gasoline'
            ]),
            'secondary_keywords': json.dumps([
                'fleet', 'vehicles', 'transportation'
            ]),
            'negative_keywords': json.dumps([
                'retail pump'
            ])
        },
        {
            'code': 'LUBRICANTS',
            'name': 'Lubricants',
            'category': 'Lubricants',
            'base_confidence_rules': json.dumps({
                'lubricantTender': 0.85,
                'maintenanceContract': 0.70
            }),
            'primary_keywords': json.dumps([
                'lubricant', 'engine oil', 'grease', 'HP Racer', 'HP Milcy'
            ]),
            'secondary_keywords': json.dumps([
                'maintenance', 'machinery', 'industrial oil'
            ]),
            'negative_keywords': json.dumps([])
        }
    ]
    
    now = datetime.now().isoformat()
    for product in products:
        # Check if exists
        c.execute('SELECT id FROM products WHERE code = ?', (product['code'],))
        existing = c.fetchone()
        
        if not existing:
            c.execute('''INSERT INTO products 
                         (code, name, category, base_confidence_rules, 
                          primary_keywords, secondary_keywords, negative_keywords,
                          scoring_factors, disqualifiers, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (product['code'], product['name'], product['category'],
                      product['base_confidence_rules'], product['primary_keywords'],
                      product['secondary_keywords'], product['negative_keywords'],
                      '{}', '{}', now))
            print(f"✅ Created product: {product['code']} - {product['name']}")
        else:
            print(f"⏭️  Product already exists: {product['code']}")
    
    conn.commit()
    conn.close()


def seed_territories():
    """Seed initial territories"""
    territories_data = [
        {
            'name': 'Mumbai West',
            'region': 'Western',
            'depot': 'Mumbai Depot',
            'coverage_areas': json.dumps(['Mumbai', 'Thane', 'Navi Mumbai', 'Kalyan']),
            'depot_lat': 19.0760,
            'depot_lng': 72.8777
        },
        {
            'name': 'Delhi NCR',
            'region': 'Northern',
            'depot': 'Delhi Depot',
            'coverage_areas': json.dumps(['Delhi', 'Noida', 'Gurgaon', 'Faridabad', 'Ghaziabad']),
            'depot_lat': 28.7041,
            'depot_lng': 77.1025
        },
        {
            'name': 'Chennai South',
            'region': 'Southern',
            'depot': 'Chennai Depot',
            'coverage_areas': json.dumps(['Chennai', 'Kanchipuram', 'Tiruvallur']),
            'depot_lat': 13.0827,
            'depot_lng': 80.2707
        }
    ]
    
    conn = db.get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    for territory in territories_data:
        try:
            c.execute('''INSERT INTO territories 
                         (name, region, depot, coverage_areas, depot_lat, depot_lng, created_at, updated_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (territory['name'], territory['region'], territory['depot'], 
                      territory['coverage_areas'], territory['depot_lat'], territory['depot_lng'],
                      now, now))
            print(f"✅ Created territory: {territory['name']}")
        except Exception as e:
            print(f"⚠️  Territory {territory['name']} might already exist: {e}")
    
    conn.commit()
    conn.close()


def main():
    """Run all seeding functions"""
    print("=" * 60)
    print("🌱 HPCL Lead Intelligence - Database Seeding")
    print("=" * 60)
    
    seed_users()
    seed_products()
    seed_territories()
    
    print("\n" + "=" * 60)
    print("✅ Seeding completed successfully!")
    print("=" * 60)
    print("\nTest credentials:")
    print("  Admin:    admin@hpcl.com / admin123")
    print("  Officer:  officer@hpcl.com / officer123")
    print("  Manager:  manager@hpcl.com / manager123")
    print("\n")


if __name__ == '__main__':
    main()
