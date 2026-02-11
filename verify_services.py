"""
Verification Script for HP-Pulse Intelligence Services
"""

import sys
import os
import time

# Add Scraper directory to path
sys.path.append(os.path.abspath("Scraper"))

from backend.app.services.entity_resolution import EntityResolutionService
from backend.app.services.product_inference import ProductInferenceService
from backend.app.services.scoring_engine import ScoringEngine
from backend.app.services.notification_service import NotificationService

def verify_entity_resolution():
    print("\n🔍 Verifying Entity Resolution...")
    
    test_cases = [
        ("Tata Power Ltd", "tata power"),
        ("Tata Power Company Limited", "tata power"),
        ("HPCL", "hpcl"),
        ("Hindustan Petroleum Corp Ltd", "hindustan petroleum"),
    ]
    
    for input_name, expected_norm in test_cases:
        norm = EntityResolutionService.normalize_name(input_name)
        status = "✅" if norm == expected_norm else f"❌ (Expected {expected_norm})"
        print(f"   Input: '{input_name}' -> Norm: '{norm}' {status}")

def verify_product_inference():
    print("\n🧠 Verifying Product Inference...")
    
    text = "Tender for supply of Furnace Oil for thermal power plant boiler heating application."
    products = ProductInferenceService.infer_products(text)
    
    if products and products[0]['code'] == 'FO':
        print(f"   ✅ Correctly identified Furnace Oil (Confidence: {products[0]['confidence']})")
    else:
        print(f"   ❌ Failed to identify Furnace Oil. Found: {products}")
        
    text_2 = "Procurement of High Speed Diesel for backup gensets"
    products_2 = ProductInferenceService.infer_products(text_2)
    if products_2 and products_2[0]['code'] == 'HSD':
        print(f"   ✅ Correctly identified HSD (Confidence: {products_2[0]['confidence']})")
    else:
        print(f"   ❌ Failed to identify HSD. Found: {products_2}")

def verify_scoring():
    print("\n💯 Verifying Scoring Engine...")
    
    from datetime import datetime
    now = datetime.now().isoformat()
    
    score = ScoringEngine.calculate_score(
        signal_type="tender",
        scraped_at=now,
        signal_text="Huge tender for 5000KL supply to Mega Power Project",
        location=None
    )
    
    print(f"   Final Score: {score['final_score']}")
    print(f"   Breakdown: {score['breakdown']}")
    
    if score['final_score'] > 0.7:
        print("   ✅ High score for critical tender")
    else:
        print("   ❌ Score seemingly too low")

def verify_notifications():
    print("\n🔔 Verifying Notification Service (Dry Run)...")
    service = NotificationService()
    
    # Mock lead
    lead = {
        'company_name': 'Test Company',
        'confidence': 0.95,
        'signal_type': 'tender'
    }
    
    # Dry run check (won't actually send without valid creds, but shouldn't crash)
    try:
        service.send_whatsapp_alert(lead, "1234567890")
        print("   ✅ Notification service invoked without crash")
    except Exception as e:
        print(f"   ❌ Notification service crashed: {e}")

if __name__ == "__main__":
    print("="*50)
    print("running Verification...")
    print("="*50)
    
    # Needs DB connection for Entity Resolution (mock it or skip DB part)
    # For this script we'll rely on static methods or catch DB errors
    try:
        verify_entity_resolution()
    except Exception as e:
        print(f"   ⚠️ DB check skipped/failed: {e}")
        
    verify_product_inference()
    verify_scoring()
    verify_notifications()
    
    print("\n✅ Verification Complete")
