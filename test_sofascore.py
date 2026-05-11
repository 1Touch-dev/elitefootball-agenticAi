import requests
import json
import re

url = "https://web.archive.org/web/2/https://www.sofascore.com/player/kendry-paez/1446114"
html = requests.get(url).text
print("HTML length:", len(html))
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
if match:
    data = json.loads(match.group(1))
    print("Found NEXT_DATA, length:", len(str(data)))
else:
    print("No NEXT_DATA found")
