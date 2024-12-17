import requests
from bs4 import BeautifulSoup
import pandas as pd
import serpapi
import json
from tqdm import tqdm
import urllib
import re

years = [2024]
venues = ['icml']
cite_query = False

for venue in venues:
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
    # print(type(soup.find_all('a', href=True)))
    print(soup.find_all('a', href=True)[10])
    raise
    paper_info = []
    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if f"/virtual/{year}/poster/" in href:
            paper_title = link.text.strip()
            print(paper_title)
            paper_id = int(href.split("/")[-1])
            authors = get_authors(venue, year, paper_id)
            if cite_query:
                # cite_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={urllib.parse.quote_plus(paper_title)}&btnG="
                # url_response = requests.get(cite_url)
                # cite_page = BeautifulSoup(url_response.content, "html.parser")
                # cite_txt = cite_page.find_all('a', string=re.compile(r'Cited by *.'))
                # cite_num = int(cite_txt[0].text[9:]) if cite_txt else 0
                params = {
                            "engine": "google_scholar",
                            "q": paper_title,
                            "api_key": "89532fd64bf9544a7c476ae2ccb2cb4fa9677301be8532e73fd77c3c7cfccb90"
                            }
                search = serpapi.search(params)
                results = search.as_dict()
                if len(results['organic_results']) > 0 and 'cited_by' in results['organic_results'][0]['inline_links']:
                    cite_num = results['organic_results'][0]['inline_links']['cited_by']['total']
                else:
                    cite_num = 0
                paper_info.append((paper_id, paper_title, authors, cite_num))
                df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors', '#cite'])
            else:
                paper_info.append((paper_id, paper_title, authors))
                df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors'])
    return df

def main():
    for venue in venues:
        for year in years:
            paper_info = get_title_authors_from_venue(venue, year)
            print(paper_info)
            if cite_query:
                paper_info.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors', '#cite'])
            else:
                paper_info.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors'])

if __name__ == "__main__":
    main()