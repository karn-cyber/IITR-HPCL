"""
Tender Scraper for HP-Pulse
Scrapes government tender portals
"""

from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from config import TENDER_KEYWORDS
from backend.app.services.entity_resolution import EntityResolutionService
from backend.app.services.product_inference import ProductInferenceService
from backend.app.services.scoring_engine import ScoringEngine
from backend.app.services.notification_service import NotificationService

class TenderScraper:
    def __init__(self, db, compliance_checker):
        self.db = db
        self.checker = compliance_checker
        self.notifier = NotificationService()
        print("✅ Tender scraper initialized")
    
    def is_relevant(self, text):
        """Check if tender is relevant"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in TENDER_KEYWORDS)
    
    def process_lead(self, company_name, signal_text, source_name, source_url, signal_type='tender'):
        """Process and save lead with intelligence services"""
        # 1. Resolve Company
        company_id = EntityResolutionService.resolve_company(
            self.db,
            name=company_name,
            industry='Government/PSU' if signal_type == 'tender' else 'General'
        )
        
        # 2. Infer Products
        products = ProductInferenceService.infer_products(signal_text)
        product_codes = [p['code'] for p in products] if products else []
        
        # 3. Calculate Score
        scraped_at = datetime.now().isoformat()
        score_data = ScoringEngine.calculate_score(
            signal_type=signal_type,
            scraped_at=scraped_at,
            signal_text=signal_text,
            location=None # TODO: Extract location
        )
        
        # 4. Insert Lead
        # Store scoring breakdown in the scoring column (as JSON) using a custom update or by formatting the insert 
        # The base insert_lead might not support the scoring breakdown column directly if it wasn't updated, 
        # so we might need to handle it. 
        # Checking database.py: insert_lead takes (company_id, signal_text, signal_type, source_name, source_url, products, confidence)
        # It DOES NOT take scoring breakdown. We need to update database.py or doing a separate update.
        # However, the extended User requested features implies we should do it right.
        # For now, let's use the confidence from the ScoringEngine as the main confidence.
        
        lead_id = self.db.insert_lead(
            company_id=company_id,
            signal_text=signal_text,
            signal_type=signal_type,
            source_name=source_name,
            source_url=source_url,
            products=product_codes,
            confidence=score_data['final_score']
        )
        
        # 5. Update with scoring breakdown (if supported by DB helper, or we hack it for now)
        # The DatabaseExtended class added a 'scoring' column. We should try to update it.
        try:
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute("UPDATE leads SET scoring = ? WHERE id = ?", 
                     (json.dumps(score_data), lead_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"   ⚠️ Could not save scoring breakdown: {e}")
            
        # 6. Send Notifications (High Confidence Only)
        if score_data['final_score'] >= 0.7:
            # Get users to notify
            try:
                users = self.db.get_notification_users({'territory': 'All'}) # Placeholder context
                
                # If no users found (e.g. no DB users yet), try to send to admin if configured
                # For hackathon demo, we might want to force send to a specific number
                # but NotificationService handles empty lists gracefully.
                
                notified_count = 0
                for user in users:
                    if user.get('phone'):
                        self.notifier.send_whatsapp_alert(
                            lead={
                                'company_name': company_name,
                                'confidence': f"{score_data['final_score']:.2f}",
                                'signal_type': signal_type
                            },
                            user_phone=user['phone']
                        )
                        notified_count += 1
                        
                if notified_count == 0 and self.notifier.wa_phone_id:
                     # Demo Fallback: Send to a default number if defined in env (Optional)
                     # Since we don't have a specific env var for "ADMIN_PHONE", we skip.
                     pass
                     
            except AttributeError:
                 # In case self.db is still the base class for some reason
                 print("   ⚠️  Database notification method missing")
            except Exception as e:
                 print(f"   ⚠️  Notification failed: {e}")

        return lead_id, products

    def scrape_cpp_portal(self, source):
        """
        Scrape CPP Portal
        Attempts to scrape public tender listings
        """
        print(f"\n🏛️  Scraping: {source['name']}")
        print(f"   URL: {source['url']}")
        
        items_found = 0
        
        try:
            # Try to access public tender search page
            search_url = "https://eprocure.gov.in/eprocure/app"
            
            response = self.checker.make_request(search_url)
            if not response:
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='tender',
                    status='error',
                    items_found=0,
                    error='Could not access portal'
                )
                print("   ⚠️  Could not access CPP Portal (may require authentication)")
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tender listings (common HTML patterns)
            tenders = soup.find_all(['div', 'tr'], class_=re.compile(r'tender|bid|rfp', re.I))
            
            if not tenders:
                # Try alternative selectors
                tenders = soup.find_all('a', href=re.compile(r'tender|bid|procurement', re.I))
            
            print(f"   Found {len(tenders)} potential tender elements")
            
            for tender_elem in tenders[:20]:  # Limit to 20
                # Extract text
                text = tender_elem.get_text(strip=True)
                
                # Check if relevant
                if self.is_relevant(text) and len(text) > 20:
                    # Try to extract company/org name
                    company_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:Ltd|Limited|Corporation|Ministry|Department))', text)
                    company_name = company_match.group(1) if company_match else "Government Organization"
                    
                    # Process Lead using new Service
                    lead_id, products = self.process_lead(
                        company_name=company_name,
                        signal_text=text[:500],
                        source_name=source['name'],
                        source_url=source['url'],
                        signal_type='tender'
                    )
                    
                    items_found += 1
                    prod_str = ", ".join([p['name'] for p in products]) if products else "No specific product"
                    print(f"   ✅ Found: {company_name} - {prod_str}")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='tender',
                status='success',
                items_found=items_found
            )
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='tender',
                status='error',
                items_found=0,
                error=str(e)
            )
        
        print(f"   📊 Total tenders found: {items_found}")
        return items_found
    
    def scrape_gem_portal(self, source):
        """
        Scrape GEM Portal
        Attempts to scrape public procurement listings
        """
        print(f"\n🏛️  Scraping: {source['name']}")
        print(f"   URL: {source['url']}")
        
        items_found = 0
        
        try:
            # Try to access GEM public pages
            response = self.checker.make_request(source['url'])
            if not response:
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='tender',
                    status='error',
                    items_found=0,
                    error='Could not access portal'
                )
                print("   ⚠️  Could not access GEM Portal (may require authentication)")
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for procurement/order listings
            orders = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'order|procurement|bid|contract', re.I))
            
            if not orders:
                orders = soup.find_all('a', href=re.compile(r'product|bid|order', re.I))
            
            print(f"   Found {len(orders)} potential order elements")
            
            for order_elem in orders[:20]:  # Limit to 20
                text = order_elem.get_text(strip=True)
                
                if self.is_relevant(text) and len(text) > 20:
                    # Extract buyer organization
                    buyer_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:Ltd|Limited|Corporation|Ministry|Organisation))', text)
                    buyer_name = buyer_match.group(1) if buyer_match else "Government Buyer"
                    
                    # Process Lead
                    lead_id, products = self.process_lead(
                        company_name=buyer_name,
                        signal_text=text[:500],
                        source_name=source['name'],
                        source_url=source['url'],
                        signal_type='tender'
                    )
                    
                    items_found += 1
                    prod_str = ", ".join([p['name'] for p in products]) if products else "No specific product"
                    print(f"   ✅ Found: {buyer_name} - {prod_str}")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='tender',
                status='success',
                items_found=items_found
            )
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='tender',
                status='error',
                items_found=0,
                error=str(e)
            )
        
        print(f"   📊 Total orders found: {items_found}")
        return items_found
    
    def scrape_all(self, sources):
        """Scrape all tender sources"""
        print("\n" + "=" * 70)
        print(f"🏛️  TENDER SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        total_items = 0
        
        for source in sources:
            if not source.get('enabled', True):
                print(f"\n⏭️  Skipping (disabled): {source['name']}")
                continue
            
            # Route to appropriate scraper
            if 'CPP' in source['name']:
                items = self.scrape_cpp_portal(source)
            elif 'GEM' in source['name']:
                items = self.scrape_gem_portal(source)
            else:
                print(f"\n⚠️  No scraper implemented for: {source['name']}")
                items = 0
            
            total_items += items
        
        print("\n" + "─" * 70)
        print(f"📊 Total tender items found: {total_items}")
        print("=" * 70)
        print()
        
        return total_items
