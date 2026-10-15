import openreview
import pandas as pd
from tqdm import tqdm
import argparse

# pip install openreview-py

YEARS = [2023, 2024, 2025, 2026]
YEARS = [2026]

SUBMISSION_TYPES = ['oral', 'spotlight', 'poster']

# Group suffixes that back each OpenReview tab:
#   tab-accept-oral      -> ICML.cc/{year}/Conference/Oral
#   tab-accept-spotlight -> ICML.cc/{year}/Conference/Spotlight
#   tab-accept-poster    -> ICML.cc/{year}/Conference/Poster
VENUE_SUFFIXES = {
    'oral':      'Oral',
    'spotlight': 'Spotlight',
    'poster':    'Poster',
}

# Fallback keyword matching when venueid is not an exact group path
TYPE_KEYWORDS = {
    'oral':      ['oral'],
    'spotlight': ['spotlight'],
    'poster':    ['poster'],
}


def get_client():
    return openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')


def get_all_submissions(client, year):
    venue_id = f'ICML.cc/{year}/Conference'
    print(f"Fetching all submissions for ICML {year}...")
    submissions = client.get_all_notes(invitation=f'{venue_id}/-/Submission')
    return submissions


def _get_val(content, field):
    v = content.get(field, '')
    if isinstance(v, dict):
        return v.get('value', '')
    return v or ''


def classify_submission(note, venue_id):
    content = note.content if hasattr(note, 'content') and note.content else {}
    venueid = _get_val(content, 'venueid')

    # Exact venueid match — directly corresponds to OpenReview tab group IDs
    for sub_type, suffix in VENUE_SUFFIXES.items():
        if venueid == f'{venue_id}/{suffix}':
            return sub_type

    # Fallback: keyword search in venue / venueid string
    venue = _get_val(content, 'venue') or venueid
    venue_lower = venue.lower()
    for sub_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in venue_lower:
                return sub_type
    return 'unknown'


def extract_paper_info(note):
    content = note.content if hasattr(note, 'content') and note.content else {}

    authors = _get_val(content, 'authors')
    if isinstance(authors, list):
        authors = ', '.join(authors)

    keywords = _get_val(content, 'keywords')
    if isinstance(keywords, list):
        keywords = ', '.join(keywords)

    return {
        'paper_id': note.id,
        'title':    _get_val(content, 'title'),
        'authors':  authors,
        'keywords': keywords,
    }


def crawl_icml(years=YEARS, types=SUBMISSION_TYPES):
    client = get_client()

    for year in years:
        venue_id = f'ICML.cc/{year}/Conference'
        print(f"\n=== ICML {year} ===")

        try:
            submissions = get_all_submissions(client, year)
            print(f"Total submissions fetched: {len(submissions)}")
        except Exception as e:
            print(f"Error fetching ICML {year}: {e}")
            continue

        classified = {t: [] for t in SUBMISSION_TYPES + ['unknown']}

        for note in tqdm(submissions, desc=f"Classifying ICML {year}"):
            sub_type = classify_submission(note, venue_id)
            classified[sub_type].append(extract_paper_info(note))

        for t, papers in classified.items():
            if papers:
                print(f"  {t}: {len(papers)} papers")

        for sub_type in types:
            papers = classified.get(sub_type, [])
            if not papers:
                print(f"  Skipping {sub_type}: no papers found")
                continue

            df = pd.DataFrame(papers)
            out_file = f'icml{year}_{sub_type}.csv'
            df.to_csv(out_file, index=False, columns=['title', 'authors', 'keywords'])
            print(f"  Saved {len(df)} papers -> {out_file}")


def main():
    parser = argparse.ArgumentParser(description='Crawl ICML papers from OpenReview')
    parser.add_argument('--years', nargs='+', type=int, default=YEARS,
                        help='Years to crawl (default: 2023 2024 2025 2026)')
    parser.add_argument('--types', nargs='+', default=SUBMISSION_TYPES,
                        choices=SUBMISSION_TYPES,
                        help='Submission types to collect (default: all)')
    args = parser.parse_args()

    crawl_icml(years=args.years, types=args.types)


if __name__ == "__main__":
    main()
