import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from tqdm import tqdm
from urllib.request import Request, urlopen

years = [2023]
proc_link = {
    2020:"https://sigir.org/sigir2020/accepted-papers/",
    2021:"https://sigir.org/sigir2021/accepted-papers/",
    2022:"https://sigir.org/sigir2022/program/accepted/",
    2023:"https://sigir.org/sigir2023/program/accepted-papers/full-papers/"
}

def get_title_authors_from_venue_2020():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = proc_link[2020]
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    paper_info_lst = []
    titles = soup.find_all('h4', class_='accepted-papers-title')
    authors = soup.find_all('h5', class_='accepted-papers-authors')
    assert len(titles) == len(authors)
    titles = [' '.join(title.text.strip().replace('\n','').split()) for title in titles]
    authors = list(map(
        lambda h5_tag: ', '.join([re.sub(r'\s+', ' ', author.strip()) \
        for author in h5_tag.text.strip().replace('\n','').split('; ')]), 
        authors))
    df = pd.DataFrame(list(zip(titles,authors)), columns=['title', 'authors'])
    return df

def get_title_authors_from_venue_2021():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = proc_link[2021]
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    soup = soup.find_all('p')
    paper_info_lst = []
    titles = [title.find('strong').text for title in soup]
    authors = [author.find('br').next_sibling for author in soup]
    assert len(titles) == len(authors)
    df = pd.DataFrame(list(zip(titles,authors)), columns=['title', 'authors'])
    return df

def get_title_authors_from_venue_2022():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = proc_link[2022]
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    soup = soup.find('div', class_='post-body').find_all('p')
    paper_info_lst = []
    titles = [title.find('b').text.strip() for title in soup if title.find('b') is not None]
    authors = [author.find('br').next_sibling.strip() for author in soup if author.find('b') is not None]
    assert len(titles) == len(authors)
    df = pd.DataFrame(list(zip(titles,authors)), columns=['title', 'authors'])
    return df

def get_title_authors_from_venue_2023():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    paper_urls = [
                "https://sigir.org/sigir2023/program/accepted-papers/full-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/short-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/perspectives-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/reproducibility-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/demo-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/resource-papers/",
                "https://sigir.org/sigir2023/program/accepted-papers/sirip-industrial-track/",
                "https://sigir.org/sigir2023/program/accepted-papers/doctoral-consortium-papers/"
                ]
    merged_paper_info = pd.DataFrame()
    for paper_url in tqdm(paper_urls):
        req = Request(paper_url,headers=hdr)
        page = urlopen(req)
        soup = BeautifulSoup(page,features="lxml")
        soup = soup.find('div', class_='avia_textblock').find_all('p')
        paper_info_lst = []
        titles = [title.find('strong').text.replace('●','').strip() for title in soup if title.find('strong') is not None]
        authors = [author.find('br').next_sibling.strip() for author in soup if author.find('strong') is not None]
        assert len(titles) == len(authors)
        df = pd.DataFrame(list(zip(titles,authors)), columns=['title', 'authors'])
        merged_paper_info = pd.concat([merged_paper_info, df], ignore_index=True)
    return merged_paper_info

def main():
    for year in years:
        if year == 2020:
            df = get_title_authors_from_venue_2020()
        elif year == 2021:
            df = get_title_authors_from_venue_2021()
        elif year == 2022:
            df = get_title_authors_from_venue_2022()
        elif year == 2023:
            df = get_title_authors_from_venue_2023()
        df.to_csv(f'sigir{year}_full.csv', index=False, columns=[
                  'title', 'authors'])

if __name__ == "__main__":
    main()