import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen

years = [2020,2021,2022,2023]
venues = ['wsdm','www','cikm','ht','umap','websci'] # ['wsdm','www','cikm','ht','umap','websci']

def get_title_authors_from_venue(venue, year):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://www.sigweb.org/toc/{venue}{str(year)[2:]}.html"
    req = Request(proc_url,headers=hdr)
    try:
        page = urlopen(req)
        print(f'{venue.upper()} {year} exists.')
    except:
        print(f'{venue.upper()} {year} does not exist.')
        return None
    soup = BeautifulSoup(page,features="lxml")
    soup = soup.find('div', {'id':'DLcontent'})
    titles = [" ".join(title.text.strip().replace('\n','').split()) for title in soup.find_all('a', class_='DLtitleLink')]
    authors = [author.text.strip().replace('\n',', ') for author in soup.find_all('ul', class_='DLauthors')]
    paper_info_lst = list(zip(titles,authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def main():
    for venue in venues:
        for year in years:
            df = get_title_authors_from_venue(venue, year)
            if df is not None:
                df.to_csv(f'{venue}{year}_full.csv', index=False, columns=[
                          'title', 'authors'])

if __name__ == "__main__":
    main()