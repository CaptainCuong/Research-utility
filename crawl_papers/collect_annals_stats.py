import argparse
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://projecteuclid.org"
JOURNAL_PATH = "journals/annals-of-statistics"

YEARS = [2026]

# projecteuclid.org sits behind Imperva/Incapsula; plain urllib requests get
# served a JS challenge page instead of content, so use requests with
# browser-like headers here.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

SKIP_CATEGORIES = {'frontmatter', 'front matter', 'backmatter', 'back matter'}


def fetch_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, features="lxml")


def get_issue_links(year):
    url = f"{BASE_URL}/{JOURNAL_PATH}/issues/{year}"
    soup = fetch_soup(url)
    pattern = re.compile(rf'^/{JOURNAL_PATH}/volume-(\d+)/issue-(\d+)$')
    issues = []
    seen = set()
    for a in soup.find_all('a', href=True):
        m = pattern.match(a['href'])
        if m and a['href'] not in seen:
            seen.add(a['href'])
            issues.append((a['href'], int(m.group(1)), int(m.group(2))))
    return issues


def get_papers_from_issue(issue_href, volume, issue, year):
    url = BASE_URL + issue_href
    soup = fetch_soup(url)
    papers = []

    for header in soup.find_all('span', class_='hangingHeader'):
        category = header.get_text(strip=True)
        if category.lower() in SKIP_CATEGORIES:
            continue

        category_row = header.find_parent('div', class_='row category')
        container = category_row.find_next_sibling('div') if category_row else None
        if container is None:
            continue

        for row in container.find_all('div', class_='TOCLineItemRow1'):
            title_tag = row.find('a', class_='TocLineItemAnchorText1')
            if title_tag is None:
                continue
            title = title_tag.get_text(strip=True)

            author_div = row.find('div', class_='TOCLineItemText2')
            authors = ''
            if author_div is not None:
                authors = ', '.join(
                    span.get_text(strip=True)
                    for span in author_div.find_all('span', class_='TOCLineItemText2')
                )
            if not authors:
                continue

            cite_tag = row.find('text', class_='TOCLineItemText3')
            citation = cite_tag.get_text(separator=' ', strip=True) if cite_tag else ''
            doi_match = re.search(r'DOI:\s*(\S+)', citation)
            doi = doi_match.group(1) if doi_match else ''

            papers.append({
                'title': title,
                'authors': authors,
                'year': year,
                'volume': volume,
                'issue': issue,
                'citation': citation,
                'doi': doi,
                'url': BASE_URL + title_tag['href'],
            })
    return papers


def crawl_year(year):
    try:
        issue_links = get_issue_links(year)
    except Exception as e:
        print(f"Error fetching issue list for {year}: {e}")
        return pd.DataFrame()

    if not issue_links:
        print(f"No issues found for {year}")
        return pd.DataFrame()

    all_papers = []
    for issue_href, volume, issue in tqdm(issue_links, desc=f"Annals of Statistics {year}"):
        try:
            all_papers.extend(get_papers_from_issue(issue_href, volume, issue, year))
        except Exception as e:
            print(f"Error fetching {issue_href}: {e}")
        time.sleep(1)

    return pd.DataFrame(all_papers)


def main():
    parser = argparse.ArgumentParser(description='Crawl Annals of Statistics papers from Project Euclid')
    parser.add_argument('--years', nargs='+', type=int, default=YEARS,
                        help='Years to crawl (default: 2026)')
    args = parser.parse_args()

    for year in args.years:
        df = crawl_year(year)
        if df.empty:
            print(f"  Skipping {year}: no papers found")
            continue
        out_file = f'annals_stats{year}_full.csv'
        df.to_csv(out_file, index=False, columns=[
            'title', 'authors', 'year', 'volume', 'issue', 'citation', 'doi', 'url'])
        print(f"  Saved {len(df)} papers -> {out_file}")


if __name__ == "__main__":
    main()
