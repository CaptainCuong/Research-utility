import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm

years = [2016,2017,2018,2019,2020,2021,2022,2023]
venue = 'cvpr'
assert venue in [
                'sigmod','pods','vldb','icde', # Database
                'www','wsdm', # World Wide Web
                'acl','naacl','coling','eacl','conll','emnlp', # NLP
                'kdd','icdm','cikm','pkdd','pakdd','sdm', # Data Mining
                'sigir','jcdl','ecir','icadl', # Information Retrieval
                'aaai','ijcai','uai','aistats','ecai', # Artificial Intelligence
                'mm', # Multimedia
                'cvpr','iccv','eccv','wacv', # Computer Vision
                'nips','icml','iclr', # Machine Learning
                'interspeech','icassp' # Speech
                ]

venue = venue.lower()
def get_links(year):
    main_url = f"https://dblp.org/db/conf/{venue}/index.html"
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")
    parts = soup.find_all("cite", itemprop="headline")
    links = []
    for part in parts:
        if str(year) in part.find("span", class_="title").get_text():
            links.append(part.find("a", class_="toc-link")['href'])
    return links

def crawl_info(url):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        pubs = soup.find_all('li',class_='entry inproceedings')
        titles = []
        authorss = []
        for pub in pubs:
            title = pub.find('span', class_='title').text.strip()[:-1]
            authors = pub.find_all('span', itemprop='author')
            authors = ','.join([author.text.strip() for author in authors])
            titles.append(title)
            authorss.append(authors)
        return titles, authorss
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)

for year in years:
    print('*'*50)
    print(f"Crawl {venue.upper()} {year}")
    links = get_links(year)
    if len(links) == 0:
        continue
    titles = []
    authorss = []
    for link in tqdm(links):
        title, authors = crawl_info(link)
        titles += title
        authorss += authors
    pd.DataFrame({"title":titles, "authors":authorss}).to_csv(f'{venue}{year}_full.csv', index=False)