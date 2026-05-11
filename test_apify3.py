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
res = requests.post("https://api.apify.com/v2/acts/apify~web-scraper/runs", json=payload, headers=headers)
print("Run start:", res.json())
import time
run_id = res.json()["data"]["id"]
while True:
    time.sleep(5)
    status = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}", headers=headers).json()
    print("Status:", status["data"]["status"])
    if status["data"]["status"] == "SUCCEEDED":
        dataset_id = status["data"]["defaultDatasetId"]
        items = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items", headers=headers).json()
        print("Items:", str(items)[:500])
        break
    if status["data"]["status"] in ("FAILED", "ABORTED"):
        break
