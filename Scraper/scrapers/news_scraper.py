"""
News Scraper for HP-Pulse
Scrapes news sources using RSS feeds and HTML parsing
"""

import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import FUEL_KEYWORDS, OPERATIONAL_KEYWORDS
from utils.company_extractor import CompanyExtractor

class NewsScraper:
    def __init__(self, db, compliance_checker):
        self.db = db
        self.checker = compliance_checker
        print("✅ News scraper initialized")
    
    def is_relevant(self, text):
        """Check if text mentions relevant keywords"""
        text_lower = text.lower()
        
        # Check for fuel keywords
        fuel_match = any(kw.lower() in text_lower for kw in FUEL_KEYWORDS)
        
        # Check for operational keywords
        ops_match = any(kw.lower() in text_lower for kw in OPERATIONAL_KEYWORDS)
        
        return fuel_match or ops_match
    
    def extract_company_name(self, title, summary):
        """Try to extract company name from news"""
        text = f"{title} {summary}"
        
        # Common patterns for Indian company names
        patterns = [
            r'([A-Z][a-zA-Z\s&]+(?:Ltd|Limited|Corporation|Corp|Inc|Industries|Chemicals|Petroleum|Energy|Power|Textiles))',
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)\s+(?:announced|plans|to|expansion|commissioning)',
            r'(Tata|Reliance|Adani|Birla|Vedanta|JSW|Essar|Ambuja|UltraTech)\s+[A-Z][a-zA-Z]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                # Clean up
                company = re.sub(r'\s+', ' ', company)
                return company
        
        return "Unknown Company"
    
    def scrape_rss(self, source):
        """Scrape RSS feed"""
        print(f"\n📰 Scraping RSS: {source['name']}")
        print(f"   URL: {source['url']}")
        
        try:
            print("   Parsing RSS feed...")
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print("   ⚠️  No entries found in RSS feed")
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='news',
                    status='success',
                    items_found=0
                )
                return 0
            
            items_found = 0
            for entry in feed.entries[:20]:  # Limit to 20 items
                title = entry.get('title', '')
                description = entry.get('description', '') or entry.get('summary', '')
                
                # Combine and check relevance
                full_text = f"{title} {description}"
                if self.is_relevant(full_text):
                    # Extract company name
                    company_name = self.extract_company_name(full_text)
                    
                    company_id = self.db.insert_company(
                        name=company_name,
                        industry='Corporate'
                    )
                    
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=f"{title}\n\n{description}",
                        signal_type='news',
                        source_name=source['name'],
                        source_url=entry.get('link', source['url']),
                        confidence=0.65
                    )
                    
                    items_found += 1
                    print(f"   ✅ Found: {title[:70]}...")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total relevant items: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0
    
    def scrape_newsapi(self, source):
        """Scrape NewsAPI for business news"""
        print(f"\n📰 Scraping NewsAPI: {source['name']}")
        
        try:
            from config import NEWSAPI_KEY
            
            if not NEWSAPI_KEY:
                print("   ⚠️  NewsAPI key not configured")
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='news',
                    status='error',
                    items_found=0,
                    error='API key not configured'
                )
                return 0
            
            # Build API request
            params = source.get('params', {})
            params['apiKey'] = NEWSAPI_KEY
            
            import requests
            response = requests.get(source['url'], params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'ok':
                print(f"   ❌ API Error: {data.get('message', 'Unknown error')}")
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='news',
                    status='error',
                    items_found=0,
                    error=data.get('message', 'API error')
                )
                return 0
            
            articles = data.get('articles', [])
            print(f"   Found {len(articles)} articles from NewsAPI")
            
            items_found = 0
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                source_name_article = article.get('source', {}).get('name', '')
                
                # Combine for relevance check
                full_text = f"{title} {description} {content}"
                
                if self.is_relevant(full_text):
                    # Extract company name using CompanyExtractor
                    company_name = self.extract_company_name(title, description if description else content)
                    
                    # Get industry from article  content
                    industry = CompanyExtractor.get_industry_from_text(full_text)
                    
                    company_id = self.db.insert_company(
                        name=company_name,
                        industry=industry
                    )
                    
                    # Create rich signal text
                    signal_text = f"{title}\n\n{description}"
                    if content and content != description:
                        signal_text += f"\n\n{content}"
                    signal_text += f"\n\nSource: {source_name_article}"
                    
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=signal_text,
                        signal_type='news',
                        source_name=f"NewsAPI - {source_name_article}",
                        source_url=article.get('url', ''),
                        confidence=0.70  # Higher confidence for verified news sources
                    )
                    
                    items_found += 1
                    print(f"   ✅ {source_name_article}: {title[:60]}...")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total relevant articles: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0

        """Scrape RSS feed"""
        print(f"\n📰 Scraping RSS: {source['name']}")
        print(f"   URL: {source['rss']}")
        
        try:
            # Parse RSS feed
            print("   Parsing RSS feed...")
            feed = feedparser.parse(source['rss'])
            
            if not feed.entries:
                print("   ⚠️  No entries found in RSS feed")
                return 0
            
            print(f"   Found {len(feed.entries)} entries")
            
            items_found = 0
            
            for entry in feed.entries[:30]:  # Limit to latest 30
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                
                # Check relevance
                if self.is_relevant(f"{title} {summary}"):
                    # Extract company name
                    company_name = self.extract_company_name(title, summary)
                    
                    # Insert company
                    company_id = self.db.insert_company(company_name)
                    
                    # Insert lead
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=f"{title}\n\n{summary}",
                        signal_type='news',
                        source_name=source['name'],
                        source_url=link,
                        confidence=0.6
                    )
                    
                    items_found += 1
                    print(f"   ✅ Relevant: {title[:70]}...")
            
            # Log success
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total relevant items: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0
    
    def scrape_html(self, source):
        """Scrape HTML-based news site"""
        print(f"\n📰 Scraping HTML: {source['name']}")
        print(f"   URL: {source['url']}")
        
        try:
            response = self.checker.make_request(source['url'])
            if not response:
                self.db.log_scrape(
                    source_name=source['name'],
                    source_type='news',
                    status='error',
                    items_found=0,
                    error='Request failed'
                )
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article headlines (generic selectors)
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'story|article|news|post'), limit=30)
            
            if not articles:
                print("   ⚠️  No articles found with standard selectors")
                # Try alternative: find all links with certain patterns
                articles = soup.find_all('a', href=re.compile(r'/news/|/article/|/story/'))[:30]
            
            print(f"   Found {len(articles)} potential articles")
            
            items_found = 0
            
            for article in articles:
                # Extract title
                if article.name == 'a':
                    title = article.get_text(strip=True)
                    link = article.get('href', '')
                else:
                    title_elem = article.find(['h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '') if title_elem.name == 'a' else ''
                
                # Make link absolute
                if link and not link.startswith('http'):
                    from urllib.parse import urljoin
                    link = urljoin(source['url'], link)
                
                # Check relevance
                if self.is_relevant(title):
                    company_name = self.extract_company_name(title, '')
                    company_id = self.db.insert_company(company_name)
                    
                    self.db.insert_lead(
                        company_id=company_id,
                        signal_text=title,
                        signal_type='news',
                        source_name=source['name'],
                        source_url=link,
                        confidence=0.5
                    )
                    
                    items_found += 1
                    print(f"   ✅ Relevant: {title[:70]}...")
            
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='success',
                items_found=items_found
            )
            
            print(f"   📊 Total relevant items: {items_found}")
            return items_found
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.db.log_scrape(
                source_name=source['name'],
                source_type='news',
                status='error',
                items_found=0,
                error=str(e)
            )
            return 0
    
    def scrape_all(self, sources):
        """Scrape all news sources"""
        print("\n" + "=" * 70)
        print(f"📰 NEWS SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        total_items = 0
        
        for source in sources:
            if not source.get('enabled', True):
                print(f"\n⏭️  Skipping (disabled): {source['name']}")
                continue
            
            # Check source type
            if source.get('type') == 'newsapi':
                items = self.scrape_newsapi(source)
            elif 'rss' in source:
                items = self.scrape_rss(source)
            else:
                items = self.scrape_html(source)
            
            total_items += items
        
        print("\n" + "─" * 70)
        print(f"📊 Total news items found: {total_items}")
        print("=" * 70)
        print()
        
        return total_items
