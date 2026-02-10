"""
Directory Scraper for HP-Pulse
Scrapes business directories for company listings
"""

from bs4 import BeautifulSoup
from datetime import datetime
import re

class DirectoryScraper:
    def __init__(self, db, compliance_checker):
        self.db = db
        self.checker = compliance_checker
        print("✅ Directory scraper initialized")
    
    def scrape_indiamart(self, source):
        """Scrape IndiaMART directory"""
        print(f"\n📋 Scraping: {source['name']}")
        print(f"   URL: {source['url']}")
        
        try:
            response = self.checker.make_request(source['url'])
            if not response:
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='directory',
                    status='error',
                    items_found=0,
                    error='Request failed'
                )
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find company listings
            # IndiaMART structure may vary, these are common selectors
            companies = soup.find_all(['div', 'li'], class_=re.compile(r'company|seller|supplier|list'))
            
            if not companies:
                # Try alternative: find company names in links
                companies = soup.find_all('a', href=re.compile(r'company|proddetail'))
            
            print(f"   Found {len(companies)} potential company listings")
            
            items_found = 0
            seen_companies = set()
            
            for comp in companies[:50]:  # Limit to first 50
                # Extract company name
                name_elem = comp.find(['h3', 'h4', 'h5', 'a', 'span'])
                if not name_elem:
                    # If company div/li, try direct text
                    name_text = comp.get_text(strip=True)
                    if len(name_text) > 100:  # Too long, probably not a company name
                        continue
                    company_name = name_text
                else:
                    company_name = name_elem.get_text(strip=True)
                
                # Clean company name
                company_name = re.sub(r'\s+', ' ', company_name)
                company_name = company_name[:200]  # Limit length
                
                # Skip if empty or already seen
                if not company_name or len(company_name) < 5:
                    continue
                if company_name in seen_companies:
                    continue
                
                seen_companies.add(company_name)
                
                # Extract location if available
                location = None
                location_patterns = [
                    re.compile(r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'),  # City, State
                    re.compile(r'(Mumbai|Delhi|Bangalore|Chennai|Kolkata|Hyderabad|Pune|Ahmedabad|Vadodara|Surat)')
                ]
                
                text = comp.get_text()
                for pattern in location_patterns:
                    match = pattern.search(text)
                    if match:
                        location = match.group(1)
                        break
                
                # Insert company
                company_id = self.db.insert_company(
                    name=company_name,
                    industry='Chemical/Manufacturing',
                    location=location
                )
                
                # Insert lead (low confidence - just a directory listing)
                self.db.insert_lead(
                    company_id=company_id,
                    signal_text=f"Company listed in {source['name']} - {source['description']}",
                    signal_type='directory',
                    source_name=source['name'],
                    source_url=source['url'],
                    confidence=0.3
                )
                
                items_found += 1
                if items_found <= 5:  # Only print first 5 to avoid clutter
                    print(f"   ✅ Found: {company_name[:60]}...")
            
            if items_found > 5:
                print(f"   ... and {items_found - 5} more")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='directory',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total companies found: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='directory',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0
    
    def scrape_tradeindia(self, source):
        """Scrape TradeIndia directory"""
        print(f"\n📋 Scraping: {source['name']}")
        print(f"   URL: {source['url']}")
        
        try:
            response = self.checker.make_request(source['url'])
            if not response:
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='directory',
                    status='error',
                    items_found=0,
                    error='Request failed'
                )
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # TradeIndia common selectors
            companies = soup.find_all(['div', 'li'], class_=re.compile(r'product|seller|company|listing'))
            
            if not companies:
                companies = soup.find_all('a', href=re.compile(r'seller|company'))
            
            print(f"   Found {len(companies)} potential company listings")
            
            items_found = 0
            seen_companies = set()
            
            for comp in companies[:50]:
                # Extract company name
                name_elem = comp.find(['h3', 'h4', 'span', 'a'])
                if name_elem:
                    company_name = name_elem.get_text(strip=True)
                else:
                    company_name = comp.get_text(strip=True)
                    if len(company_name) > 100:
                        continue
                
                company_name = re.sub(r'\s+', ' ', company_name)[:200]
                
                if not company_name or len(company_name) < 5 or company_name in seen_companies:
                    continue
                
                seen_companies.add(company_name)
                
                # Insert company
                company_id = self.db.insert_company(
                    name=company_name,
                    industry='Petroleum/Chemicals'
                )
                
                # Insert lead
                self.db.insert_lead(
                    company_id=company_id,
                    signal_text=f"Company listed in {source['name']} - {source['description']}",
                    signal_type='directory',
                    source_name=source['name'],
                    source_url=source['url'],
                    confidence=0.3
                )
                
                items_found += 1
                if items_found <= 5:
                    print(f"   ✅ Found: {company_name[:60]}...")
            
            if items_found > 5:
                print(f"   ... and {items_found - 5} more")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='directory',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total companies found: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='directory',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0

    
    def scrape_all(self, sources):
        """Scrape all directory sources"""
        print("\n" + "=" * 70)
        print(f"📋 DIRECTORY SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        total_items = 0
        
        for source in sources:
            if not source.get('enabled', True):
                print(f"\n⏭️  Skipping (disabled): {source['name']}")
                continue
            
            if 'indiamart' in source['url'].lower():
                items = self.scrape_indiamart(source)
            elif 'tradeindia' in source['url'].lower():
                items = self.scrape_tradeindia(source)
            else:
                print(f"\n⚠️  No scraper implemented for: {source['name']}")
                items = 0
            
            total_items += items
        
        print("\n" + "─" * 70)
        print(f"📊 Total directory items found: {total_items}")
        print("=" * 70)
        print()
        
        return total_items
