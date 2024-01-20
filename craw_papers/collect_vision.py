import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm

years = [2023]
venues = ['ICCV']

venues = list(map(str.upper,venues))
for venue in venues:
    assert venue in ['CVPR','WACV','ICCV']

def crawl_save_proceedings(venue, year):
    url = f"https://openaccess.thecvf.com/{venue}{year}?day=all"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    titles = []
    authors = []
    pp_board = soup.find('dl').find_all(recursive=False)

    i = 0
    while i < len(pp_board):
        tag_class = pp_board[i].get('class')
        if tag_class and tag_class[0] == 'ptitle':
            titles.append(pp_board[i].find('a').text)
            authors.append(', '.join([at.text for at in pp_board[i+1].find_all('a')]))
            i += 1
        i += 1

    pd.DataFrame({'title':titles,'authors':authors}).to_csv(f'{venue.lower()}{year}_full.csv',index=False)

def main():
    for venue in venues:
        for year in years:
            crawl_save_proceedings(venue, year)

if __name__ == "__main__":
    main()