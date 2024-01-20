import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
import urllib
import re

years = [2020]
venues = ['iclr']
cite_query = False

assert venue in ['neurips','icml','iclr']

def get_authors(venue, year, paper_id):
    url = f"https://{venue}.cc/virtual/{year}/poster/{paper_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        script_text = script_tag.string.strip()
        script_data = json.loads(script_text)
        authors = (', ').join([author['name']
                               for author in script_data['author']])

    return authors


def get_title_authors_from_venue(venue, year):
    url = f"https://{venue}.cc/virtual/{year}/papers.html?filter=titles"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paper_info = []
    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if f"/virtual/{year}/poster/" in href:
            paper_title = link.text.strip()
            paper_id = int(href.split("/")[-1])
            authors = get_authors(venue, year, paper_id)
            if cite_query:
                cite_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={urllib.parse.quote_plus(paper_title)}&btnG="
                url_response = requests.get(cite_url)
                cite_page = BeautifulSoup(url_response.content, "html.parser")
                cite_txt = cite_page.find_all('a', string=re.compile(r'Cited by *.'))
                cite_num = int(cite_txt[0].text[9:]) if cite_txt else 0
                paper_info.append((paper_id, paper_title, authors, cite_num))
                df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors', '#cite'])
            else:
                paper_info.append((paper_id, paper_title, authors))
                df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors'])
    return df


def main():
    for venue in venues:
        for year in years:
            df = get_title_authors_from_venue(venue, year)
            if cite_query:
                df.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors', '#cite'])
            else:
                df.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors'])

if __name__ == "__main__":
    main()