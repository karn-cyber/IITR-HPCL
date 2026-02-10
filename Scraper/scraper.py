#!/usr/bin/env python3
"""
HP-Pulse Scraper
B2B Lead Intelligence System for HPCL Direct Sales

Scheduled scraper that monitors:
- Government tenders (every 1 hour)
- News sources (every 6 hours)
- Business directories (every 24 hours)
"""

import schedule
import time
from datetime import datetime
import sys

# Import configuration
from config import SOURCES

# Import utilities
from utils.database import Database
from utils.compliance import ComplianceChecker

# Import scrapers
from scrapers.tender_scraper import TenderScraper
from scrapers.news_scraper import NewsScraper
from scrapers.directory_scraper import DirectoryScraper
from scrapers.selenium_scraper import SeleniumScraper

class HPPulseScraper:
    def __init__(self):
        print("\n" + "=" * 70)
        print("🚀 Initializing HP-Pulse Scraper...")
        print("=" * 70)
        
        # Initialize database
        print("\n📦 Setting up database...")
        self.db = Database()
        
        # Initialize compliance checker
        print("🛡️  Setting up compliance checker...")
        self.checker = ComplianceChecker()
        
        # Initialize scrapers
        print("🕷️  Setting up scrapers...")
        self.tender_scraper = TenderScraper(self.db, self.checker)
        self.news_scraper = NewsScraper(self.db, self.checker)
        self.directory_scraper = DirectoryScraper(self.db, self.checker)
        self.selenium_scraper = SeleniumScraper(self.db, self.checker)
        print("✅ Tender scraper initialized")
        print("✅ News scraper initialized")
        print("✅ Directory scraper initialized")
        print("✅ Selenium scraper initialized")
        
        print("\n✅ Initialization complete!")
        print("=" * 70)
    
    def scrape_tenders(self):
        """Job: Scrape tender sources"""
        try:
            sources = SOURCES['tenders']['sources']
            self.tender_scraper.scrape_all(sources)
            
            # Run Selenium deep scraping
            self.scrape_tenders_selenium()
        except Exception as e:
            print(f"❌ Error in tender scraping: {e}")
    
    def scrape_tenders_selenium(self):
        """Job: Deep scrape tenders with Selenium"""
        try:
            # Find sources with selenium enabled
            selenium_sources = [
                s for s in SOURCES['tenders']['sources']
                if s.get('selenium', False) and s.get('enabled', True)
            ]
            
            if selenium_sources:
                for source in selenium_sources:
                    self.selenium_scraper.scrape_cpp_portal_tenders(source)
                
                # Close driver after all selenium scraping
                self.selenium_scraper.close_driver()
        except Exception as e:
            print(f"❌ Error in Selenium scraping: {e}")
    
    def scrape_news(self):
        """Job: Scrape news sources"""
        try:
            sources = SOURCES['news']['sources']
            self.news_scraper.scrape_all(sources)
        except Exception as e:
            print(f"❌ Error in news scraping: {e}")
    
    def scrape_directories(self):
        """Job: Scrape directory sources"""
        try:
            sources = SOURCES['directories']['sources']
            self.directory_scraper.scrape_all(sources)
        except Exception as e:
            print(f"❌ Error in directory scraping: {e}")
    
    def print_schedule(self):
        """Print scraping schedule"""
        print("\n" + "=" * 70)
        print(" " * 20 + "HP-PULSE SCRAPER")
        print(" " * 15 + "B2B Lead Intelligence System")
        print(" " * 18 + "For HPCL Direct Sales")
        print("=" * 70)
        print()
        print("⏰ SCRAPING SCHEDULE:")
        print()
        
        # Tenders
        tender_interval = SOURCES['tenders']['interval_hours']
        tender_count = len([s for s in SOURCES['tenders']['sources'] if s.get('enabled', True)])
        print(f"   🏛️  TENDERS:")
        print(f"       Interval: Every {tender_interval} hour(s)")
        print(f"       Sources:  {tender_count} active")
        for source in SOURCES['tenders']['sources']:
            if source.get('enabled', True):
                print(f"         • {source['name']}")
        print()
        
        # News
        news_interval = SOURCES['news']['interval_hours']
        news_count = len([s for s in SOURCES['news']['sources'] if s.get('enabled', True)])
        print(f"   📰 NEWS:")
        print(f"       Interval: Every {news_interval} hour(s)")
        print(f"       Sources:  {news_count} active")
        for source in SOURCES['news']['sources']:
            if source.get('enabled', True):
                print(f"         • {source['name']}")
        print()
        
        # Directories
        dir_interval = SOURCES['directories']['interval_hours']
        dir_count = len([s for s in SOURCES['directories']['sources'] if s.get('enabled', True)])
        print(f"   📋 DIRECTORIES:")
        print(f"       Interval: Every {dir_interval} hour(s)")
        print(f"       Sources:  {dir_count} active")
        for source in SOURCES['directories']['sources']:
            if source.get('enabled', True):
                print(f"         • {source['name']}")
        
        print()
        print("=" * 70)
    
    def run(self):
        """Start the scheduler"""
        self.print_schedule()
        
        # Schedule jobs
        print("\n📅 Setting up schedule...")
        schedule.every(SOURCES['tenders']['interval_hours']).hours.do(self.scrape_tenders)
        schedule.every(SOURCES['news']['interval_hours']).hours.do(self.scrape_news)
        schedule.every(SOURCES['directories']['interval_hours']).hours.do(self.scrape_directories)
        
        # Run immediately on start
        print("\n🔄 Running initial scrape cycle...")
        print("   This may take a few minutes...\n")
        
        self.scrape_tenders()
        self.scrape_news()
        self.scrape_directories()
        
        # Show summary
        stats = self.db.get_stats()
        print("\n" + "=" * 70)
        print("📊 INITIAL SCRAPE COMPLETE")
        print("=" * 70)
        print(f"   Total Companies: {stats['total_companies']}")
        print(f"   Total Leads:     {stats['total_leads']}")
        print()
        
        # Keep running
        print("=" * 70)
        print("🔄 Scheduler now running...")
        print("   Next scrapes will run according to schedule")
        print("   Press Ctrl+C to stop")
        print("=" * 70)
        print()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("👋 HP-Pulse Scraper stopped by user")
            
            # Final stats
            final_stats = self.db.get_stats()
            print()
            print("📊 FINAL STATISTICS:")
            print(f"   Total Companies: {final_stats['total_companies']}")
            print(f"   Total Leads:     {final_stats['total_leads']}")
            print(f"   Today's Leads:   {final_stats['today_leads']}")
            print()
            print("   Data saved to: hp_pulse.db")
            print("   Run 'python monitor.py' to view dashboard")
            print("=" * 70)
            sys.exit(0)

def main():
    """Main entry point"""
    print("\n🌟 Welcome to HP-Pulse Scraper!")
    print("   Developed for HPCL Productathon 2026")
    print()
    
    try:
        scraper = HPPulseScraper()
        scraper.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("   Please check your configuration and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
