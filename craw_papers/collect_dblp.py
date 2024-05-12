import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm

years = [2016,2017,2018,2019,2020,2021,2022,2023,2024]
years = [2020,2021,2022,2023,2024]

confs = [
        'sigmod','pods','vldb','icde', # Database
        'www','wsdm', # World Wide Web
        'acl','naacl','colingconf','eacl','conll','emnlp', # NLP
        'kdd','icdm','cikm','pkdd','pakdd','sdm', # Data Mining
        'sigir','jcdl','ecir','icadl', # Information Retrieval
        'aaai','ijcai','uai','aistats','ecai', # Artificial Intelligence
        'mm', # Multimedia
        'iros','icra','atal', # Reinforcement Learning
        'cvpr','iccv','eccv','wacv', # Computer Vision
        'nips','icml','iclr', # Machine Learning
        'interspeech','icassp' # Speech
        'sp','tifsconf','ccs','uss','ndss', # Security
        ]

journals = [
            "ai", # Artificial Intelligence
            "colingjour", # Computational Linguistics
            "datamine", # Data Mining and Knowledge Discovery
            "tkde", # IEEE Transactions on Knowledge and Data Engineering
            "tnn", # IEEE Transactions on Neural Networks and Learning Systems
            "pami", # IEEE Transactions on Pattern Analysis and Machine Intelligence
            "tip", # IEEE Transactions on Image Processing
            "ijcv", # International Journal of Computer Vision
            "tsp", # IEEE Transactions on Signal Processing
            "jmlr", # Journal of Machine Learning Research
            "paa", # Pattern Analysis and Applications
            "tmi", # IEEE transactions on medical imaging
            "tcyb", # IEEE Transactions on Systems, Man, and Cybernetics
            "mia", # Medical Image Analysis
            "natmi", # Nature Machine Intelligence
            "pr", # Neural Networks
            "kbs", # Knowledge-Based Systems
            "compsec", # Computers & Security
            "ieeesp", # IEEE Security & Privacy
            "tdsc", # IEEE Transactions on Dependable and Secure Computing
            "tifsjour", # IEEE Transactions on Information Forensics and Security
            "istr", # Journal of Information Security and Applications
            "csur", # ACM Computing Surveys
            ]

venues = [
          "colingconf"
         ]

def get_links(venue, year):
    journal = False
    if venue in journals:
        journal = True
        if venue in ["colingjour", "tifsjour"]:
            venue = venue[:-4]
    else:
        if venue in ["colingconf", "tifsconf"]:
            venue = venue[:-4]

    if journal:
        main_url = f"https://dblp.org/db/journals/{venue}/index.html"
    else:
        main_url = f"https://dblp.org/db/conf/{venue}/index.html"
    
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    if journal:
        parts = soup.find("div", id="info-section").find_next_siblings("ul")[0]
        parts = parts.find_all("li")
        for part in  parts:
            if str(year) in part.get_text():
                for month in part.find_all("a"):
                    links.append(month['href'])
    else:
        if venue == "colingconf":
            venue = "coling"
        parts = soup.find_all("cite", itemprop="headline")
        for part in parts:
            if str(year) in part.find("span", class_="title").get_text():
                links.append(part.find("a", class_="toc-link")['href'])
    return links

def crawl_info(url):
    # Send a GET request to the URL
    response = requests.get(url)
    conf = "conf" in url
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <p> tags
        titles = []
        authorss = []
        if conf:
            pubs = soup.find_all('li',class_='entry inproceedings')
        else:
            pubs = soup.find_all('cite',class_='data tts-content')
        for pub in pubs:
            title = pub.find('span', class_='title').text.strip()[:-1]
            authors = pub.find_all('span', itemprop='author')
            authors = ', '.join([author.text.strip() for author in authors])
            titles.append(title)
            authorss.append(authors)
        return titles, authorss
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)

for venue in venues:
    venue = venue.lower()
    assert venue in confs or venue in journals
    for year in years:
        print('*'*50)
        print(f"Crawl {venue.upper()} {year}")
        links = get_links(venue, year)
        if len(links) == 0:
            continue
        titles = []
        authorss = []
        for link in tqdm(links):
            title, authors = crawl_info(link)
            titles += title
            authorss += authors
        pd.DataFrame({"title":titles, "authors":authorss}).to_csv(f'{venue}{year}_full.csv', index=False)