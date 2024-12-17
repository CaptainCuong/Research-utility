import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen
import re

years = [2023,2022,2021,2020]
venues = ['UAI','AISTATS','COLT','CoRL'] # ['ACML','UAI','AISTATS','COLT','CoRL','ALT']
s
def access_venue(venue, year):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://proceedings.mlr.press/"
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    soup = soup.find_all('ul', class_='proceedings-list')[-1].find_all('li')
    venue_links = []
    for link in soup:
        if link.find('a') is not None and f'{venue} {year}' in link.get_text():
            venue_links.append("https://proceedings.mlr.press/" + link.find('a')['href'])
    if venue_links == []:
        print(f'{venue.upper()} {year} does not exist.')
        return None
    paper_info_lst = pd.DataFrame()
    for venue_link in venue_links:
        req = Request(venue_link,headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page,features="lxml")
        paper_info_lst = pd.concat([paper_info_lst, get_title_authors_from_venue(soup)], ignore_index=True)
    return paper_info_lst

def get_title_authors_from_venue(soup):
    paper_info_lst = []
    for paper_info in tqdm(soup.find_all('div', class_='paper')):
        paper_title = re.sub(r'[\r\n"\']','', paper_info.find('p', class_='title').get_text().strip())
        authors = re.sub(r'[\r\n"\' ]','', paper_info.find('span', class_='authors').get_text().strip())
        paper_info_lst.append((paper_title, authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def main():
    for venue in venues:
        for year in years:
            df = access_venue(venue, year)
            if df is not None:
                df.to_csv(f'{venue.lower()}{year}_full.csv', index=False, columns=[
                          'title', 'authors'])

if __name__ == "__main__":
    main()