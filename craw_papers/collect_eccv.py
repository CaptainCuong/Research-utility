import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

years = [2016,2018,2020]

def get_links(year):
    main_url = "https://dblp.org/db/conf/eccv/index.html"
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")
    parts = soup.find_all("cite", itemprop="headline")
    links = []
    for part in parts:
        if f"ECCV {year}" in part.find("span", class_="title").get_text():
            links.append(part.find("a", class_="toc-link")['href'])
    return links

def crawl_info(url):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        pubs = soup.find_all('li',class_='entry inproceedings')
        titles = []
        authorss = []
        for pub in pubs:
            title = pub.find('span', class_='title').text.strip()[:-1]
            authors = pub.find_all('span', itemprop='author')
            authors = ','.join([author.text.strip() for author in authors])
            titles.append(title)
            authorss.append(authors)
        return titles, authorss
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)

for year in years:
    if year % 2 == 1:
        continue
    links = get_links(year)
    titles = []
    authorss = []
    for link in links:
        title, authors = crawl_info(link)
        titles += title
        authorss += authors
    pd.DataFrame({"title":titles, "authors":authorss}).to_csv(f'eccv{year}_full.csv', index=False)