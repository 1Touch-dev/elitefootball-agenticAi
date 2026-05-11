import sys, os, time
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scraping.fbref import scrape_fbref_page
from scripts.player_urls import ALL_PLAYER_URLS

def main():
    print(f"Scraping FBref data for {len(ALL_PLAYER_URLS)} players using archive.org...")
    for slug, urls in ALL_PLAYER_URLS.items():
        fbref_url = urls.get("fbref")
        if fbref_url:
            print(f"Scraping FBref for {slug}...")
            try:
                res = scrape_fbref_page(fbref_url, slug=slug, headless=True)
                print(f"  Success! Parsed matches: {len(res.get('stats', []))}")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(1)
        
if __name__ == "__main__":
    main()
