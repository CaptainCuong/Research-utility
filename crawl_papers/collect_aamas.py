import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse

YEARS = [2022, 2023, 2024, 2025]

# Maps our track name -> keyword(s) used to identify the section heading.
# Heading text differs slightly by year (e.g. "Full Papers" vs "Research Paper
# Track", "Demonstration Track" vs "Demo Track"), so match on a substring
# instead of the exact heading.
TRACKS = {
    'keynote': 'keynote',
    'full_papers': 'paper',
    'demo': 'demo',
    'jaamas': 'jaamas',
}


def get_sections(soup):
    """Return [(track_name, [paper_p, ...]), ...].

    The page lays papers out across several <table> rows (a "Return to Top"
    row is inserted periodically), so consecutive papers are NOT always
    siblings in the DOM. We instead take all <p> tags in document order and
    slice between heading <p> tags (the ones carrying an <a name=...> bookmark).
    """
    all_ps = soup.find_all('p')
    heading_indices = []  # (index_in_all_ps, track_name)
    for i, p in enumerate(all_ps):
        if p.find('a', attrs={'name': True}) is None:
            continue
        heading_text = p.get_text(' ', strip=True).lower()
        for track, keyword in TRACKS.items():
            if keyword in heading_text:
                heading_indices.append((i, track))
                break

    sections = []
    for idx, (start_i, track) in enumerate(heading_indices):
        end_i = heading_indices[idx + 1][0] if idx + 1 < len(heading_indices) else len(all_ps)
        paper_ps = [p for p in all_ps[start_i + 1:end_i] if p.find('a', href=True)]
        sections.append((track, paper_ps))
    return sections


def parse_papers(paper_ps):
    titles = []
    authorss = []
    for node in paper_ps:
        link = node.find('a', href=True)
        title = ' '.join(link.get_text(' ', strip=True).split())
        fonts = node.find_all('font')
        authors = []
        if fonts:
            for text_node in fonts[-1].find_all(string=True, recursive=False):
                name = ' '.join(text_node.split())
                if name:
                    authors.append(name)
        titles.append(title)
        authorss.append(', '.join(authors))
    return titles, authorss


def crawl_year(year):
    url = f"https://www.ifaamas.org/Proceedings/aamas{year}/forms/contents.htm"
    print('*' * 50)
    print(f"Crawl AAMAS {year}: {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("  Failed to retrieve the page. Status code:", response.status_code)
        return
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
    sections = get_sections(soup)
    found_tracks = {track for track, _ in sections}
    for track in TRACKS:
        if track not in found_tracks:
            print(f"  Track '{track}' not found for {year}, skipping")

    all_titles = []
    all_authors = []
    for track, paper_ps in sections:
        titles, authors = parse_papers(paper_ps)
        if not titles:
            print(f"  {track}: 0 papers found")
            continue
        out_file = f'aamas{year}_{track}.csv'
        pd.DataFrame({"title": titles, "authors": authors}).to_csv(out_file, index=False)
        print(f"  {track}: saved {len(titles)} papers -> {out_file}")
        all_titles += titles
        all_authors += authors

    if all_titles:
        full_file = f'aamas{year}_full.csv'
        pd.DataFrame({"title": all_titles, "authors": all_authors}).to_csv(full_file, index=False)
        print(f"  all tracks: saved {len(all_titles)} papers -> {full_file}")


def main():
    parser = argparse.ArgumentParser(description='Crawl AAMAS papers from ifaamas.org proceedings contents pages')
    parser.add_argument('--years', nargs='+', type=int, default=YEARS,
                         help='Years to crawl (default: 2022 2023 2024 2025)')
    args = parser.parse_args()

    for year in args.years:
        crawl_year(year)


if __name__ == "__main__":
    main()
