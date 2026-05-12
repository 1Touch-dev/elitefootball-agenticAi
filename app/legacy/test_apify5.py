import requests, os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("APIFY_API_TOKEN")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
url = "https://fbref.com/en/players/82f14376/Kendry-Paez"
payload = {
    "startUrls": [{"url": url}],
    "pageFunction": "async function pageFunction(context) { return {html: await context.page.content()}; }",
    "proxyConfiguration": {"useApifyProxy": True}
}
try:
    res = requests.post("https://api.apify.com/v2/acts/apify~playwright-scraper/runs", json=payload, headers=headers)
    print("Run start:", res.json())
except Exception as e:
    print("Error:", e)
