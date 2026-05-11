import sys, os, time
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scraping.apify_fallback import fetch_fbref_player
from scripts.player_urls import IDV_PLAYER_URLS

def main():
    print("Scraping FBref data for 5 IDV players using Apify Playwright Scraper...")
    for slug, url in list(IDV_PLAYER_URLS.items())[:5]:
        print(f"Scraping {slug}...")
        res = fetch_fbref_player(slug.replace("-", " "), None)
        print(f"Result for {slug}: has_stats={bool(res.get('stats'))}, error={res.get('error')}")
        
if __name__ == "__main__":
    main()
