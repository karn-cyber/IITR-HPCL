"""
Enhanced Tender Scraper for CPP Portal
Scrapes actual tender details including organization, value, dates
Based on browser research of portal structure
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

class EnhancedTenderScraper:
    def __init__(self, db, compliance_checker):
        self.db = db
        self.compliance = compliance_checker
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
    
    def scrape_cpp_tenders_by_organization(self):
        """
        Scrape CPP Portal using 'Tenders by Organisation' approach
        This bypasses captcha and gets real tender details
        """
        print("\n🏛️  Enhanced CPP Portal Scraper - Real Tender Details")
        
        base_url = "https://eprocure.gov.in/eprocure/app"
        org_page_url = f"{base_url}?page=FrontEndTendersByOrganisation&service=page"
        
        tenders_found = 0
        
        try:
            # Step 1: Get organizations list page
            print(f"   📋 Fetching organizations list...")
            response = self.session.get(org_page_url, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"   ❌ Failed to fetch organizations page")
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Find organization links with tender counts
            # Look for table with organizations
            org_tables = soup.find_all('table')
            organizations = []
            
            for table in org_tables:
                rows = table.find_all('tr')
                for row in rows[1:10]:  # First 10 orgs only for speed
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        org_name_cell = cells[0]
                        count_cell = cells[1] if len(cells) > 1 else None
                        
                        # Extract organization name
                        org_name = org_name_cell.get_text(strip=True)
                        
                        # Extract tender count and link
                        if count_cell:
                            count_link = count_cell.find('a')
                            if count_link and count_link.get('href'):
                                tender_count = count_link.get_text(strip=True)
                                organizations.append({
                                    'name': org_name,
                                    'count': tender_count,
                                    'url': count_link['href']
                                })
            
            print(f"   📊 Found {len(organizations)} organizations with active tenders")
            
            # Step 3: For each organization, fetch their tenders
            for org in organizations[:3]:  # Limit to 3 orgs for now
                print(f"\n   🏢 Organization: {org['name']} ({org['count']} tenders)")
                
                # Construct full URL for organization's tenders
                org_tender_url = f"{base_url}{org['url']}" if org['url'].startswith('?') else org['url']
                
                time.sleep(1)  # Rate limiting
                
                try:
                    org_response = self.session.get(org_tender_url, verify=False, timeout=15)
                    org_soup = BeautifulSoup(org_response.content, 'html.parser')
                    
                    # Find tender listing table
                    tender_tables = org_soup.find_all('table')
                    
                    for table in tender_tables:
                        tender_rows = table.find_all('tr')
                        
                        for row in tender_rows[1:6]:  # First 5 tenders per org
                            cells = row.find_all('td')
                            
                            if len(cells) >= 4:
                                # Extract tender info from table
                                tender_title = cells[0].get_text(strip=True) if len(cells) > 0 else "N/A"
                                tender_ref = cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
                                published_date = cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
                                closing_date = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"
                                
                                # Clean up title
                                tender_title = tender_title[:200] if tender_title else "Tender"
                                
                                # Create rich tender details
                                tender_details = {
                                    'title': tender_title,
                                    'reference': tender_ref,
                                    'organization': org['name'],
                                    'published_date': published_date,
                                    'closing_date': closing_date,
                                    'portal': 'CPP Portal',
                                    'value': 'To be disclosed',  # Not in listing, need detail page
                                }
                                
                                # Check if relevant to fuel/petroleum
                                full_text = f"{tender_title} {org['name']}"
                                if self.is_fuel_related(full_text):
                                    # Insert into database
                                    company_id = self.db.insert_company(
                                        name=org['name'],
                                        industry='Government/PSU'
                                    )
                                    
                                    signal_text = f"{tender_title}\n\n"
                                    signal_text += f"Organization: {org['name']}\n"
                                    signal_text += f"Reference No: {tender_ref}\n"
                                    signal_text += f"Published: {published_date}\n"
                                    signal_text += f"Closing Date: {closing_date}\n"
                                    signal_text += f"Portal: CPP Portal (eprocure.gov.in)"
                                    
                                    self.db.insert_lead(
                                        company_id=company_id,
                                        signal_text=signal_text,
                                        signal_type='tender',
                                        source_name='CPP Portal - Enhanced Scraper',
                                        source_url=org_tender_url,
                                        confidence=0.90
                                    )
                                    
                                    tenders_found += 1
                                    print(f"      ✅ {tender_title[:60]}... | {org['name']}")
                
                except Exception as e:
                    print(f"   ⚠️  Error fetching tenders for {org['name']}: {e}")
                    continue
            
            print(f"\n   📊 Total detailed tenders found: {tenders_found}")
            return tenders_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 0
    
    def is_fuel_related(self, text):
        """Check if tender is related to fuel/petroleum/chemicals"""
        keywords = ['fuel', 'petroleum', 'diesel', 'petrol', 'oil', 'gas', 'lpg', 'chemical', 'energy']
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
