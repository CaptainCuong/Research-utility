import requests
from bs4 import BeautifulSoup
import pandas as pd
import serpapi
import json
from tqdm import tqdm
import urllib
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

years = [2026]
venues = ['icml']
cite_query = False

for venue in venues:
    assert venue in ['neurips','icml','iclr']

def create_session_with_retries():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_authors(venue, year, paper_id, session):
    url = f"https://{venue}.cc/virtual/{year}/poster/{paper_id}"
    try:
        time.sleep(0.2)  # Reduced delay to speed up processing
        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            script_text = script_tag.string.strip()
            script_data = json.loads(script_text)
            authors = (', ').join([author['name']
                                   for author in script_data['author']])
            return authors
        return "Unknown"
    except Exception as e:
        print(f"\nError fetching authors for paper {paper_id}: {e}")
        time.sleep(2)  # Longer sleep on error before retry
        return "Unknown"

def get_title_authors_from_venue(venue, year, save_interval=100):
    session = create_session_with_retries()
    url = f"https://{venue}.cc/virtual/{year}/papers.html?filter=titles"

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching papers list: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")
    # print(type(soup.find_all('a', href=True)))
    print(soup.find_all('a', href=True)[10])
    paper_info = []
    paper_count = 0

    for link in tqdm(soup.find_all('a', href=True)):
        href = link['href']
        if f"/virtual/{year}/poster/" in href:
            paper_title = link.text.strip()
            # print(paper_title)  # Commented out to reduce console spam
            paper_id = int(href.split("/")[-1])
            authors = get_authors(venue, year, paper_id, session)
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
            else:
                paper_info.append((paper_id, paper_title, authors))

            # Periodic save to avoid losing progress
            paper_count += 1
            if paper_count % save_interval == 0:
                df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors', '#cite'] if cite_query else ['paper_id', 'title', 'authors'])
                df.to_csv(f'{venue}{year}_full_temp.csv', index=False, columns=['title', 'authors', '#cite'] if cite_query else ['title', 'authors'])
                print(f"\nProgress saved: {paper_count} papers processed")

    df = pd.DataFrame(paper_info, columns=['paper_id', 'title', 'authors', '#cite'] if cite_query else ['paper_id', 'title', 'authors'])
    return df

def main():
    for venue in venues:
        for year in years:
            paper_info = get_title_authors_from_venue(venue, year)
            print(f"\nTotal papers collected: {len(paper_info)}")
            if cite_query:
                paper_info.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors', '#cite'])
            else:
                paper_info.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors'])
            print(f"Saved to {venue}{year}_full.csv")

if __name__ == "__main__":
    main()