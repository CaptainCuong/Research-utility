import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from urllib.request import Request, urlopen

years = [2020,2021,2022,2023]
proc_link = {
	2020:"https://www.kdd.org/kdd2020/proceedings/",
	2021:"https://kdd.org/kdd2021/accepted-papers/toc",
	2022:"https://kdd.org/kdd2022/toc.html",
	2023:"https://kdd.org/kdd2023/wp-content/uploads/2023/08/toc.html"
}

def ul_to_authors(ul_tag):
	authors = [li_tag.text.strip() for li_tag in ul_tag.find_all('li',class_='nameList')]
	return ', '.join(authors)

def get_title_authors_from_venue(year):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    proc_url = proc_link[year]
    req = Request(proc_url,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page,features="lxml")
    paper_info_lst = []
    titles = soup.find_all('a', class_='DLtitleLink')
    authors = soup.find_all('ul', class_='DLauthors')
    assert len(titles) == len(authors)
    titles = [' '.join(title.text.strip().replace('\n','').split()) for title in titles]
    authors = list(map(ul_to_authors, authors))
    df = pd.DataFrame(list(zip(titles,authors)), columns=['title', 'authors'])
    return df

def main():
    for year in years:
        df = get_title_authors_from_venue(year)
        df.to_csv(f'kdd{year}_full.csv', index=False, columns=[
                  'title', 'authors'])

if __name__ == "__main__":
    main()