import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen

years = [2023,2022,2021,2020]

def access_venue(year):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://aistats.org/aistats{year}/accepted.html"
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    paper_info_lst = get_title_authors_from_venue(soup)
    return paper_info_lst

def get_title_authors_from_venue(soup):
    paper_info_lst = []
    for paper_info in tqdm(soup.find_all('ul')[-1].find_all('li')):
        paper_title = paper_info.find('b').get_text().strip()
        authors = paper_info.find('br').next_sibling.strip()
        paper_info_lst.append((paper_title, authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def main():
    for year in years:
        df = access_venue(year)
        df.to_csv(f'aistats{year}_full.csv', index=False, columns=[
                  'title', 'authors'])

if __name__ == "__main__":
    main()