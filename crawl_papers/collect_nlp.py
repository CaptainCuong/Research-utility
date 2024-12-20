import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
import urllib
import re
import time
import random

years = [2024]
venues = ['acl']
cite_query = False
for venue in venues:
    assert venue in ['acl','emnlp','anlp','naacl','eacl','aacl','alta','bionlp','blackboxnlp','clinicalnlp','eamt','amta','textgraphs']

def crawl_save_proceedings(venue, year):
    url = f"https://aclanthology.org/events/{venue}-{year}/"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    titles = []
    authors = []
    cite = []
    for para in tqdm(soup.find_all('span', class_='d-block')[5:]):
        title = para.find('a', href=True)
        if f'/{year}' not in title['href']:
            continue
        author = [at.text for at in para.find_all('a') if '/people' in at['href']]
        if len(author) == 0:
            continue
        if cite_query:
            cite_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={urllib.parse.quote_plus(title.text)}&btnG="
            url_response = requests.get(cite_url)
            cite_page = BeautifulSoup(url_response.content, "html.parser")
            cite_txt = cite_page.find_all('a', string=re.compile(r'Cited by *.'))
            cite_num = int(cite_txt[0].text[9:]) if len(cite_txt)>0 else 0
            cite.append(cite_num)
            time.sleep(random.randint(50, 150))
        titles.append(title.text)
        authors.append(', '.join(author))

    if cite_query:
        pd.DataFrame({'title':titles,'authors':authors,'#cite':cite}).to_csv(f'{venue}{year}_full.csv',index=False)
    else:
        pd.DataFrame({'title':titles,'authors':authors}).to_csv(f'{venue}{year}_full.csv',index=False)

def main():
    for venue in venues:
        for year in years:
            crawl_save_proceedings(venue, year)

if __name__ == "__main__":
    main()