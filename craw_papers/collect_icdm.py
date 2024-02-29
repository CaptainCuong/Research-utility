import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

years = [2018,2019,2020,2021,2024]

def crawl_info2024(url):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        paragraphs = soup.find_all('ul')[6].find_all('li')
        # Extract text from paragraphs that start with "DM"
        title_authors = [extract_title_and_authors2024(p) for p in paragraphs]
        title_authors = list(zip(*title_authors))
        title = list(title_authors[0])
        authors = list(title_authors[1])
        return title, authors
    else:
        raise
        print("Failed to retrieve the page. Status code:", response.status_code)

def extract_title_and_authors2024(li_html):
    # Extract title from <a> tag
    title = li_html.a.get_text()
    # Extract authors from <span> tag and remove unnecessary characters
    authors = li_html.span.get_text().replace('*', '').replace('; ', ',').strip()
    return title, authors

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
        return pd.DataFrame({'title':titles,'authors':authorss})
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)

for year in years:
    if year != 2024:
        url = f"https://dblp.org/db/conf/icdm/icdm{year}.html"
        df = crawl_info(url)
        df.to_csv(f'icdm{year}_full.csv', index=False, columns=['title', 'authors'])
    else:
        url = "https://icde2024.github.io/papers.html"
        titles, authorss = crawl_info2024(url)
        pd.DataFrame({'title':titles, 'authors':authorss}).to_csv(f'icdm{year}_full.csv', index=False, columns=[
                          'title', 'authors'])