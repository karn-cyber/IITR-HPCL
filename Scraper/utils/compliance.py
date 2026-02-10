"""
Compliance checker for policy-safe web scraping
"""

import requests
import time
from datetime import datetime
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from config import USER_AGENT, REQUEST_TIMEOUT

class ComplianceChecker:
    def __init__(self):
        self.last_request_times = {}  # domain -> timestamp
        self.robots_cache = {}        # domain -> RobotFileParser
        print("✅ Compliance checker initialized")
    
    def check_robots_txt(self, url):
        """Check if URL is allowed by robots.txt"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Check cache
        if domain in self.robots_cache:
            rp = self.robots_cache[domain]
            can_fetch = rp.can_fetch("*", url)
            return can_fetch
        
        # Fetch and parse robots.txt
        try:
            rp = RobotFileParser()
            rp.set_url(f"{domain}/robots.txt")
            rp.read()
            self.robots_cache[domain] = rp
            
            can_fetch = rp.can_fetch("*", url)
            
            if not can_fetch:
                print(f"⚠️  Blocked by robots.txt: {domain}")
            else:
                print(f"✓ robots.txt allows scraping: {domain}")
            
            return can_fetch
        except Exception as e:
            print(f"⚠️  Could not fetch robots.txt for {domain}: {e}")
            # If can't fetch robots.txt, assume allowed but be cautious
            return True
    
    def rate_limit(self, domain, min_interval=1.0):
        """Ensure minimum interval between requests to same domain"""
        if domain in self.last_request_times:
            elapsed = time.time() - self.last_request_times[domain]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                print(f"⏳ Rate limiting {domain}: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_request_times[domain] = time.time()
    
    def make_request(self, url, headers=None, timeout=REQUEST_TIMEOUT):
        """Make a compliant HTTP request"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Check robots.txt
        if not self.check_robots_txt(url):
            print(f"❌ Skipping {url} - blocked by robots.txt")
            return None
        
        # Rate limit
        self.rate_limit(domain)
        
        # Make request
        try:
            default_headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            if headers:
                default_headers.update(headers)
            
            print(f"🌐 Fetching: {url}")
            response = requests.get(url, headers=default_headers, timeout=timeout)
            response.raise_for_status()
            
            print(f"✓ Response: {response.status_code} ({len(response.content)} bytes)")
            return response
            
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout for {url}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error for {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for {url}: {e}")
            return None
    
    def log_provenance(self, url, data_extracted):
        """Log data provenance (source + timestamp)"""
        return {
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'data': data_extracted
        }
