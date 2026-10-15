#!/usr/bin/env python3
"""
Download all NeurIPS 2026 accepted papers into neurips2026_papers.csv
with columns: title,authors
 
Usage:  pip install requests   (if needed)
        python neurips2026_papers.py         # papers only -> neurips2026_papers.csv
        python neurips2026_papers.py --all   # every event -> neurips2026_all_events.csv
                                             #   (title,authors,type; no filtering/dedup)
 
Source: the JSON feed behind https://neurips.cc/virtual/2026/papers.html
(the same data shown on https://neurips.cc/Downloads/2026).
"""
import csv
import sys
 
import requests
 
YEAR = 2026
OUT = f"neurips{YEAR}_papers.csv"
URL = f"https://neurips.cc/static/virtual/data/neurips-{YEAR}-orals-posters.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (paper-list export script)"}
 
 
def author_names(authors):
    names = []
    for a in authors or []:
        if isinstance(a, dict):
            n = a.get("fullname") or a.get("name") or ""
        else:
            n = str(a)
        n = " ".join(n.split())
        if n:
            names.append(n)
    return ", ".join(names)
 
 
def main():
    all_events = "--all" in sys.argv
    out = f"neurips{YEAR}_all_events.csv" if all_events else OUT
    r = requests.get(URL, headers=HEADERS, timeout=120)
    r.raise_for_status()
    data = r.json()
    items = data.get("results", data) if isinstance(data, dict) else data
 
    # Skip only clearly non-paper events; keep everything else
    NON_PAPER = ("workshop", "tutorial", "invited", "keynote", "talk",
                 "demonstration", "demo", "competition", "social", "affinity",
                 "expo", "panel", "town hall", "break", "meetup")
 
    from collections import Counter
    kept_types, dropped_types = Counter(), Counter()
    rows, seen = [], set()
    for it in items:
        etype = (it.get("eventtype") or it.get("event_type") or "").strip()
        if not all_events and any(w in etype.lower() for w in NON_PAPER):
            dropped_types[etype] += 1
            continue
        title = " ".join((it.get("name") or it.get("title") or "").split())
        if not title:
            continue
        authors = author_names(it.get("authors"))
        key = (title.lower(), authors.lower())
        if not all_events and key in seen:  # an oral also appears as its poster
            continue
        seen.add(key)
        kept_types[etype or "(none)"] += 1
        rows.append((title, authors, etype) if all_events else (title, authors))
 
    print(f"Entries in feed: {len(items)}")
    print("Kept by event type:   ", dict(kept_types))
    print("Dropped by event type:", dict(dropped_types))
 
    rows.sort(key=lambda r: r[0].lower())
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["title", "authors", "type"] if all_events else ["title", "authors"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} {'events' if all_events else 'papers'} to {out}")
 
 
if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        sys.exit(f"Could not fetch {URL}: {e}\n"
                 "Fallback: open https://neurips.cc/Downloads/2026, tick "
                 "'Posters', choose csv and download.")