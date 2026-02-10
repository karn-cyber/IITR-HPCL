#!/usr/bin/env python3
"""
Run Scraper Once
Executes a single pass of all configured scrapers and exits.
"""
import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import HPPulseScraper

def main():
    print("🚀 Starting single-pass scrape...")
    
    try:
        scraper = HPPulseScraper()
        
        print("\n📥 Scraping Tenders...")
        scraper.scrape_tenders()
        
        print("\n📰 Scraping News...")
        scraper.scrape_news()
        
        print("\n📋 Scraping Directories...")
        scraper.scrape_directories()
        
        print("\n✅ Scrape complete!")
        
        # Show stats
        stats = scraper.db.get_stats()
        print("\n📊 STATISTICS:")
        print(f"   Total Companies: {stats['total_companies']}")
        print(f"   Total Leads:     {stats['total_leads']}")
        print(f"   Today's Leads:   {stats['today_leads']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
