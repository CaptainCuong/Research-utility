import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm

year = 2023
venue = 'acl'
assert venue in ['acl','emnlp','anlp','aacl','alta','bionlp','blackboxnlp','clinicalnlp','eamt','amta','textgraphs']

url = f"https://aclanthology.org/events/{venue}-{year}/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

titles = []
authors = []
for para in tqdm(soup.find_all('span', class_='d-block')):
    title = para.find('a', href=True)
    if f'/{year}' not in title['href']:
        continue
    author = [at.text for at in para.find_all('a') if '/people' in at['href']]
    if len(author) == 0:
        continue
    titles.append(title.text)
    authors.append(', '.join(author))
pd.DataFrame({'title':titles,'authors':authors}).to_csv(f'{venue}{year}_full.csv',index=False)