import asyncio
from app.scraping.crawl4ai_engine import Crawl4AIEngine

async def main():
    engine = Crawl4AIEngine()
    res = await engine.fetch_page("https://fbref.com/en/players/82f14376/Kendry-Paez")
    print("Success:", res.get("success"))
    print("HTML length:", len(res.get("html", "")))
    print("Error:", res.get("error"))

asyncio.run(main())
