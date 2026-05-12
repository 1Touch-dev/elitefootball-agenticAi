import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
url = "https://api.tavily.com/extract"
payload = {"api_key": api_key, "urls": ["https://fbref.com/en/players/82f14376/Kendry-Paez"]}
res = requests.post(url, json=payload).json()
print("Extract results:", res)
