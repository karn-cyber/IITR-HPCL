"""
Tender Scraper for HP-Pulse
Scrapes government tender portals
"""

from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import TENDER_KEYWORDS

class TenderScraper:
    def __init__(self, db, compliance_checker):
        self.db = db
        self.checker = compliance_checker
        print("✅ Tender scraper initialized")
    
    def is_relevant(self, text):
        """Check if tender is relevant"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in TENDER_KEYWORDS)
    
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
                    
                    # Insert company
                    company_id = self.db.insert_company(
                        name=company_name,
                        industry='Government/PSU'
                    )
                    
                    # Insert lead
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=text[:500],  # Limit text length
                        signal_type='tender',
                        source_name=source['name'],
                        source_url=source['url'],
                        confidence=0.85
                    )
                    
                    items_found += 1
                    print(f"   ✅ Found: {text[:70]}...")
            
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
                    
                    company_id = self.db.insert_company(
                        name=buyer_name,
                        industry='Government'
                    )
                    
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=text[:500],
                        signal_type='tender',
                        source_name=source['name'],
                        source_url=source['url'],
                        confidence=0.80
                    )
                    
                    items_found += 1
                    print(f"   ✅ Found: {text[:70]}...")
            
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
