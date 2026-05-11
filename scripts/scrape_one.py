import sys, os, time
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scraping.fbref import scrape_fbref_page
from app.scraping.sofascore import scrape_sofascore_page

def main():
    print("Scraping FBref and Sofascore for Kendry Paez...")
    
    fbref_url = "https://fbref.com/en/players/82f14376/Kendry-Paez"
    print(f"Scraping FBref: {fbref_url}")
    try:
        res = scrape_fbref_page(fbref_url, slug="kendry-paez", headless=True)
        print("Success FBref!")
    except Exception as e:
        print(f"Error FBref: {e}")
        
    sofascore_url = "https://www.sofascore.com/player/kendry-paez/1446114"
    print(f"Scraping Sofascore: {sofascore_url}")
    try:
        res = scrape_sofascore_page(sofascore_url, slug="kendry-paez")
        print("Success Sofascore!")
    except Exception as e:
        print(f"Error Sofascore: {e}")

if __name__ == "__main__":
    main()
