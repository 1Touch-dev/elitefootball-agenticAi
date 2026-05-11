from app.scraping.crawl4ai_engine import crawl_page
res = crawl_page("https://fbref.com/en/players/82f14376/Kendry-Paez")
print("Success:", res.get("success"))
html = res.get("html", "")
print("HTML length:", len(html))
print("Error:", res.get("error"))
