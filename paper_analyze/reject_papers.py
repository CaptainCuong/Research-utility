import requests

response = requests.get(
    "https://api.openreview.net/notes",
    headers={},
)
data = response.json()