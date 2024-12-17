import requests
from bs4 import BeautifulSoup

# URL of the page you want to scrape
url = "https://openreview.net/forum?id=fjZMGKB2dU"

# Send a GET request to the website
response = requests.get(url)

# Parse the page content
soup = BeautifulSoup(response.content, "html.parser")
print(soup)
# Find all elements that contain paper titles
# (This will vary depending on the HTML structure of the page)
titles = soup.find_all("h4")  # Assuming titles are in <h4> tags

# Print all paper titles
for title in titles:
    print(title.get_text())
