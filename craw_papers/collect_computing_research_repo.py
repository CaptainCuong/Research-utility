import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm

years = [2024]
months = [3]

def crawl_info(year, month):
    url = f"https://dblp.org/db/journals/corr/corr{str(year)[2:]}{month:02}.html"

    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        titles = []
        authorss = []
        print(f"Collect Computing Research Repo (Year {year})")
        pubs = soup.find_all('cite',class_='data tts-content')
        for pub in tqdm(pubs):
            title = pub.find('span', class_='title').text.strip()[:-1]
            authors = pub.find_all('span', itemprop='author')
            authors = ', '.join([author.text.strip() for author in authors])
            titles.append(title)
            authorss.append(authors)
        return titles, authorss
    else:
        print(f"Failed to retrieve year {year}, month {month}.")

for year in years:
    print(f"Collect Computing Research Repo (Year {year})")
    titles = []
    authorss = []
    for month in months:
        title, authors = crawl_info(year, month)
        titles += title
        authorss += authors
        pd.DataFrame({"title":titles, "authors":authorss}).to_csv(f'corr{year}_full.csv', index=False)