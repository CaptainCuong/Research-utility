import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm

years = [2023,2022,2021,2020]

def get_title_authors_from_ijcai(year):
    url = f"https://www.ijcai.org/proceedings/{year}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paper_info = []
    for paper in tqdm(soup.find_all('div', class_="paper_wrapper")):
        paper_title = paper.find_all('div', class_="title")[0].text
        authors = paper.find_all('div', class_="authors")[0].text
        paper_info.append((paper_title, authors))
    df = pd.DataFrame(paper_info, columns=['title', 'authors'])
    return df

def main():
    for year in years:
        df_ijcai = get_title_authors_from_ijcai(year)
        df_ijcai.to_csv(f'ijcai{year}_full.csv', index=False, columns=[
                  'title', 'authors'])

if __name__ == "__main__":
    main()