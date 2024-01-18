import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen

year = 2019

def access_venue():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://proceedings.mlr.press/"
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    soup = soup.find_all('ul', class_='proceedings-list')[-1].find_all('li')
    for link in soup:
        if link.find('a') is not None and f'UAI {year}' in link.get_text():
            venue_link = "https://proceedings.mlr.press/" + link.find('a')['href']
            continue
    req = Request(venue_link,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    paper_info_lst = get_title_authors_from_venue(soup)
    return paper_info_lst

def get_title_authors_from_venue(soup):
    paper_info_lst = []
    for paper_info in tqdm(soup.find_all('div', class_='paper')):
        paper_title = paper_info.find('p', class_='title').get_text().strip()
        authors = paper_info.find('span', class_='authors').get_text().strip().replace(' ', '')
        paper_info_lst.append((paper_title, authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def main():
    df = access_venue()
    df.to_csv(f'uai{year}_full.csv', index=False, columns=[
              'title', 'authors'])


if __name__ == "__main__":
    main()