import os
from dotenv import load_dotenv
load_dotenv()
from app.scraping.apify_fallback import fetch_page_html
print("APIFY_API_TOKEN:", os.getenv("APIFY_API_TOKEN")[:5] + "...")
html = fetch_page_html("https://fbref.com/en/players/82f14376/Kendry-Paez")
print("HTML length:", len(html))
print("HTML sample:", html[:200])
