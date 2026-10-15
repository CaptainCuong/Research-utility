import openreview
import pandas as pd
from tqdm import tqdm
import argparse

# pip install openreview-py

YEARS = [2025, 2026]

SUBMISSION_TYPES = ['oral', 'spotlight', 'poster', 'reject', 'withdrawn', 'desk_rejected']

TYPE_KEYWORDS = {
    'oral':         ['oral'],
    'spotlight':    ['spotlight'],
    'poster':       ['poster'],
    'reject':       ['reject', 'rejected'],
    'withdrawn':    ['withdrawn'],
    'desk_rejected': ['desk reject'],
}


def get_client():
    return openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')


def get_all_submissions(client, year):
    venue_id = f'ICLR.cc/{year}/Conference'
    print(f"Fetching all submissions for ICLR {year}...")
    submissions = client.get_all_notes(invitation=f'{venue_id}/-/Submission')
    return submissions


def _get_val(content, field):
    v = content.get(field, '')
    if isinstance(v, dict):
        return v.get('value', '')
    return v or ''


def classify_submission(note):
    content = note.content if hasattr(note, 'content') and note.content else {}
    venue = _get_val(content, 'venue')
    if not venue:
        venue = _get_val(content, 'venueid')
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
        'abstract': _get_val(content, 'abstract'),
        'keywords': keywords,
        'venue':    _get_val(content, 'venue'),
    }


def crawl_iclr(years=YEARS, types=SUBMISSION_TYPES):
    client = get_client()

    for year in years:
        print(f"\n=== ICLR {year} ===")

        try:
            submissions = get_all_submissions(client, year)
            print(f"Total submissions fetched: {len(submissions)}")
        except Exception as e:
            print(f"Error fetching ICLR {year}: {e}")
            continue

        classified = {t: [] for t in SUBMISSION_TYPES + ['unknown']}

        for note in tqdm(submissions, desc=f"Classifying ICLR {year}"):
            sub_type = classify_submission(note)
            classified[sub_type].append(extract_paper_info(note))

        for t, papers in classified.items():
            if papers:
                print(f"  {t}: {len(papers)} papers")

        for sub_type in types:
            papers = classified.get(sub_type, [])
            if not papers:
                print(f"  Skipping {sub_type}: no papers found")
                continue

            df = pd.DataFrame(papers).drop(columns=['abstract', 'venue'], errors='ignore')
            out_file = f'iclr{year}_{sub_type}.csv'
            df.to_csv(out_file, index=False, columns=['title', 'authors', 'keywords'])
            print(f"  Saved {len(df)} papers -> {out_file}")


def main():
    parser = argparse.ArgumentParser(description='Crawl ICLR papers from OpenReview')
    parser.add_argument('--years', nargs='+', type=int, default=YEARS,
                        help='Years to crawl (default: 2025 2026)')
    parser.add_argument('--types', nargs='+', default=SUBMISSION_TYPES,
                        choices=SUBMISSION_TYPES,
                        help='Submission types to collect (default: all)')
    args = parser.parse_args()

    crawl_iclr(years=args.years, types=args.types)


if __name__ == "__main__":
    main()
