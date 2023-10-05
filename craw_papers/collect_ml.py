import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm

year = 2022
venue = 'iclr'

assert venue in ['neurips','icml','iclr']

def get_authors(paper_id):
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


def get_title_authors_from_venue():
    url = f"https://{venue}.cc/virtual/{year}/papers.html?filter=titles"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paper_info = []
    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if f"/virtual/{year}/poster/" in href:
            paper_title = link.text.strip()
            paper_id = int(href.split("/")[-1])
            authors = get_authors(paper_id)
            paper_info.append((paper_id, paper_title, authors))
    df = pd.DataFrame(paper_info, columns=['paper_id', 'title',  'authors'])
    return df


def main():
    df = get_title_authors_from_venue()
    df.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
              'title', 'authors'])


if __name__ == "__main__":
    main()