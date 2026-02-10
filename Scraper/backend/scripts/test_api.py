#!/usr/bin/env python3
"""
Manual API Test Script

This script tests the backend API endpoints manually without needing all dependencies installed.
Run this after the API server is started.
"""

import urllib.request
import urllib.parse
import json


API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        req = urllib.request.Request(f"{API_BASE}/health")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"✅ Health check passed: {data}")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_login():
    """Test login endpoint"""
    print("\n" + "=" * 60)
    print("Testing Login Endpoint")
    print("=" * 60)
    
    credentials = {
        "email": "admin@hpcl.com",
        "password": "admin123"
    }
    
    try:
        data = json.dumps(credentials).encode('utf-8')
        req = urllib.request.Request(
            f"{API_BASE}/api/auth/login",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"✅ Login successful!")
            print(f"   Token: {result['token'][:50]}...")
            print(f"   User: {result['user']['name']} ({result['user']['role']})")
            return result['token']
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None


def test_get_leads(token):
    """Test get leads endpoint"""
    print("\n" + "=" * 60)
    print("Testing Get Leads Endpoint")
    print("=" * 60)
    
    try:
        req = urllib.request.Request(
            f"{API_BASE}/api/leads?page=1&limit=5",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"✅ Leads retrieved successfully!")
            print(f"   Total leads: {result['pagination']['total']}")
            print(f"   Page: {result['pagination']['page']}/{result['pagination']['totalPages']}")
            print(f"   Leads on this page: {len(result['leads'])}")
            
            if result['leads']:
                lead = result['leads'][0]
                print(f"\n   First lead:")
                print(f"   - ID: {lead['id']}")
                print(f"   - Company: {lead['company']}")
                print(f"   - Confidence: {lead['confidence']}")
                print(f"   - Source: {lead['source']}")
            
            return True
    except Exception as e:
        print(f"❌ Get leads failed: {e}")
        return False


def test_dashboard_stats(token):
    """Test dashboard stats endpoint"""
    print("\n" + "=" * 60)
    print("Testing Dashboard Stats Endpoint")
    print("=" * 60)
    
    try:
        req = urllib.request.Request(
            f"{API_BASE}/api/dashboard/stats?dateRange=7d",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"✅ Dashboard stats retrieved successfully!")
            print(f"   Total leads: {result['summary']['totalLeads']}")
            print(f"   High confidence: {result['summary']['highConfidence']}")
            print(f"   Auto assigned: {result['summary']['autoAssigned']}")
            print(f"   Estimated value: ${result['summary']['estimatedValue']:,.2f}")
            
            if result.get('byCategory'):
                print(f"\n   Leads by category:")
                for category, count in list(result['byCategory'].items())[:5]:
                    print(f"   - {category}: {count}")
            
            return True
    except Exception as e:
        print(f"❌ Dashboard stats failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("🧪 HPCL Lead Intelligence - API Manual Test")
    print("=" * 60)
    print("\n⚠️  Make sure the API server is running on port 8000!")
    print("   Start it with: python3 -m uvicorn backend.app.main:app --reload\n")
    
    # Test health
    if not test_health():
        print("\n❌ API server is not running. Please start it first.")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login failed. Cannot test authenticated endpoints.")
        print("   Make sure you've run the seed script: python3 backend/scripts/seed_data.py")
        return
    
    # Test authenticated endpoints
    test_get_leads(token)
    test_dashboard_stats(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Open http://localhost:8000/docs for interactive API testing")
    print("  2. Use the token to test other endpoints")
    print("  3. Check the full API documentation in backend/README.md")
    print("\n")


if __name__ == '__main__':
    main()
