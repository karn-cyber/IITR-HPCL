"""
Selenium-based scraper for deep tender extraction
Extracts detailed tender information from CPP Portal
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime


class SeleniumScraper:
    """Selenium-based scraper for dynamic content"""
    
    def __init__(self, db, compliance_checker):
        self.db = db
        self.compliance = compliance_checker
        self.driver = None
    
    def setup_driver(self):
        """Initialize Chrome WebDriver with headless mode"""
        print("🌐 Initializing Selenium WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Install and setup ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        print("✅ WebDriver initialized")
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("🔒 WebDriver closed")
    
    def scrape_cpp_portal_tenders(self, source):
        """Deep scrape CPP Portal for detailed tender information by navigating organization pages"""
        print(f"\n🔍 Deep scraping: {source['name']} (Selenium)")
        
        if not self.driver:
            self.setup_driver()
        
        try:
            url = "https://eprocure.gov.in/eprocure/app"
            print(f"   📍 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            tenders_found = 0
            
            # Step 1: Click "Tenders by Organisation"
            try:
                print("   🔎 Looking for 'Tenders by Organisation' link...")
                org_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Tenders by Organisation")
                org_link.click()
                time.sleep(3)
                print("   ✅ Opened Tenders by Organisation page")
                
                # Step 2: Find organization tables
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
                
                organizations = []
                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows[1:15]:  # First 15 organizations
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 2:
                                org_name = cells[0].text.strip()
                                count_link = cells[1].find_element(By.TAG_NAME, "a")
                                tender_count = count_link.text.strip()
                                
                                if org_name and org_name not in ['Screen Reader', 'Search', '']:
                                    organizations.append({
                                        'name': org_name,
                                        'count': tender_count,
                                        'element': count_link
                                    })
                        except:
                            continue
                
                print(f"   📊 Found {len(organizations)} organizations")
                
                # Step 3: For each organization, extract tenders
                for i, org in enumerate(organizations[:5]):  # Process first 5 orgs
                    try:
                        print(f"\n   🏢 Organization {i+1}: {org['name']} ({org['count']} tenders)")
                        
                        # Click on organization
                        org['element'].click()
                        time.sleep(3)
                        
                        # Extract tenders from this organization
                        tender_rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr")
                        
                        for row in tender_rows[1:11]:  # First 10 tenders per org
                            try:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                
                                if len(cells) >= 5:
                                    # Extract data from table columns
                                    tender_title = cells[3].text.strip() if len(cells) > 3 else "Tender"
                                    ref_no = cells[3].text.split('\n')[1] if '\n' in cells[3].text else "N/A"
                                    pub_date = cells[0].text.strip() if len(cells) > 0 else "N/A"
                                    closing_date = cells[1].text.strip() if len(cells) > 1 else "N/A"
                                    opening_date = cells[2].text.strip() if len(cells) > 2 else "N/A"
                                    
                                    # Clean title
                                    if '\n' in tender_title:
                                        title_parts = tender_title.split('\n')
                                        tender_title = title_parts[0]
                                        ref_no = title_parts[1] if len(title_parts) > 1 else ref_no
                                    
                                    # Store in database - NO FILTERING, GET ALL TENDERS
                                    company_id = self.db.insert_company(
                                        name=org['name'],
                                        industry='Government/PSU'
                                    )
                                    
                                    signal_text = f"{tender_title}\n\n"
                                    signal_text += f"Organization: {org['name']}\n"
                                    signal_text += f"Reference No: {ref_no}\n"
                                    signal_text += f"Published Date: {pub_date}\n"
                                    signal_text += f"Closing Date: {closing_date}\n"
                                    signal_text += f"Opening Date: {opening_date}\n"
                                    signal_text += f"Portal: CPP Portal (eprocure.gov.in)"
                                    
                                    self.db.insert_lead(
                                        company_id=company_id,
                                        signal_text=signal_text,
                                        signal_type='tender',
                                        source_name=source['name'] + ' (Selenium)',
                                        source_url=self.driver.current_url,
                                        confidence=0.90
                                    )
                                    
                                    tenders_found += 1
                                    print(f"      ✅ {tender_title[:50]}... | {closing_date}")
                            
                            except Exception as e:
                                continue
                        
                        # Go back to organizations list
                        self.driver.back()
                        time.sleep(2)
                    
                    except Exception as e:
                        print(f"      ⚠️  Error with {org['name']}: {str(e)[:50]}")
                        continue
            
            except Exception as e:
                print(f"   ❌ Error navigating organizations: {e}")
            
            # Log scrape
            self.db.log_scrape(
                source_name=source['name'] + ' (Selenium)',
                source_type='tender',
                status='success',
                items_found=tenders_found
            )
            
            print(f"\n   📊 Total detailed tenders extracted: {tenders_found}")
            return tenders_found
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'] + ' (Selenium)',
                source_type='tender',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0
    
    def is_relevant_tender(self, text):
        """Check if tender text is relevant to fuel/petroleum"""
        text_lower = text.lower()
        
        keywords = [
            'fuel', 'diesel', 'petrol', 'petroleum', 'oil', 'lubricant',
            'hsd', 'furnace', 'bitumen', 'hexane', 'chemical',
            'refinery', 'energy', 'power', 'generator'
        ]
        
        return any(keyword in text_lower for keyword in keywords)
    
    def extract_tender_details(self, text):
        """Extract structured details from tender text"""
        details = {}
        
        # Extract title (first line or first 100 chars)
        lines = text.split('\n')
        details['title'] = lines[0][:100] if lines else text[:100]
        
        # Try to extract organization name
        org_patterns = [
            r'(?:by|from)\s+([A-Z][A-Za-z\s&]+(?:Ltd|Limited|Corporation|Department|Ministry))',
            r'([A-Z][A-Za-z\s]+(?:Department|Ministry|Corporation))'
        ]
        
        for pattern in org_patterns:
            match = re.search(pattern, text)
            if match:
                details['organization'] = match.group(1).strip()
                break
        
        # Try to extract value
        value_patterns = [
            r'(?:Rs\.?|INR|₹)\s*([\d,\.]+)\s*(?:Cr|Crore|Lakh|Lakhs)?',
            r'([\d,]+)\s*(?:Crore|Lakh)',
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text)
            if match:
                details['value'] = match.group(0)
                break
        
        # Try to extract deadline
        deadline_patterns = [
            r'(?:deadline|due|closing|last date)[:\s]*([\d\-/]+)',
            r'(\d{2}[-/]\d{2}[-/]\d{4})'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['deadline'] = match.group(1)
                break
        
        details['description'] = ' '.join(lines[1:3]) if len(lines) > 1 else text[:200]
        
        return details if details.get('title') else None
