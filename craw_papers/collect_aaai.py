import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen

years = [2023,2022,2021,2020]

def get_title_authors_from_venue(year):
    proc_num = 36 + year-2022
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://aaai.org/proceeding/aaai-{proc_num}-{year}/"
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    track_urls = [track_info['href'] for track_info in soup.find_all('a', href=True) if 'No.' in track_info.getText()]
    paper_info_lst = []
    for track_url in track_urls:
        req = Request(track_url,headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page,features="lxml")
        for paper_info in tqdm(soup.find_all('li', class_="paper-wrap")):
            paper_title = paper_info.find('h5').find('a').get_text()
            authors = paper_info.find('span').find('p').get_text()
            paper_info_lst.append((paper_title, authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def get_title_authors_from_venue_2023():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = f"https://ojs.aaai.org/index.php/AAAI/issue/archive"
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    track_urls = [track_info['href'] for track_info in soup.find_all('a', href=True) if 'AAAI-23' in track_info.getText()]
    paper_info_lst = []
    for track_url in track_urls:
        req = Request(track_url,headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page,features="lxml")
        for paper_info in tqdm(soup.find_all('div', class_="obj_article_summary")):
            paper_title = paper_info.find('h3').find('a').get_text().strip()
            authors = paper_info.find('div', class_="authors").get_text().strip()
            paper_info_lst.append((paper_title, authors))
    df = pd.DataFrame(paper_info_lst, columns=['title', 'authors'])
    return df

def main():
    for year in years:
        if year != 2023:
            df = get_title_authors_from_venue(year)
        else:
            df = get_title_authors_from_venue_2023()
        df.to_csv(f'aaai{year}_full.csv', index=False, columns=[
                  'title', 'authors'])

if __name__ == "__main__":
    main()