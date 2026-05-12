import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.scraping.unified_scraper import fetch_via_tavily
from dotenv import load_dotenv
load_dotenv()
res = fetch_via_tavily("Kendry Paez fbref.com stats")
for item in res:
    print(item.get('url'), len(item.get('content', '')))
