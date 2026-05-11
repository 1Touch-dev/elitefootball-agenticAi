import sys, os, time
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scraping.sofascore import scrape_sofascore_page
from scripts.player_urls import ALL_PLAYER_URLS

def main():
    print(f"Scraping Sofascore data for {len(ALL_PLAYER_URLS)} players...")
    for slug, urls in ALL_PLAYER_URLS.items():
        sofascore_url = urls.get("sofascore")
        if sofascore_url:
            print(f"Scraping Sofascore for {slug}...")
            try:
                res = scrape_sofascore_page(sofascore_url, slug=slug)
                print(f"  Success! Parsed matches: {len(res.get('player_match_stats', []))}")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(1)
        
if __name__ == "__main__":
    main()
