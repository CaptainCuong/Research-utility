import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import os
import time
import urllib.parse

def search_and_download_acl_paper(title, output_dir='papers'):
    """
    Search for a paper by title on ACL Anthology and download its PDF

    Args:
        title: Paper title
        output_dir: Directory to save the PDF

    Returns:
        tuple: (success: bool, pdf_path: str or None, message: str)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Search on ACL Anthology
        search_url = f"https://aclanthology.org/search/?q={urllib.parse.quote_plus(title)}"
        response = requests.get(search_url, timeout=30)

        if response.status_code != 200:
            return False, None, f"Search failed with status code {response.status_code}"

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the first paper result
        paper_links = soup.find_all('a', class_='align-middle')
        if not paper_links:
            return False, None, "No papers found in search results"

        # Get the paper page URL
        paper_url = "https://aclanthology.org" + paper_links[0]['href']

        # Visit the paper page to get PDF link
        paper_response = requests.get(paper_url, timeout=30)
        if paper_response.status_code != 200:
            return False, None, f"Failed to access paper page: {paper_response.status_code}"

        paper_soup = BeautifulSoup(paper_response.content, "html.parser")

        # Find PDF link
        pdf_link = paper_soup.find('a', class_='btn btn-primary', string='PDF')
        if not pdf_link:
            return False, None, "PDF link not found on paper page"

        pdf_url = pdf_link['href']
        if not pdf_url.startswith('http'):
            pdf_url = "https://aclanthology.org" + pdf_url

        # Download PDF
        pdf_response = requests.get(pdf_url, timeout=60)
        if pdf_response.status_code != 200:
            return False, None, f"Failed to download PDF: {pdf_response.status_code}"

        # Save PDF with sanitized filename
        safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename[:100]  # Limit filename length
        pdf_path = os.path.join(output_dir, f"{safe_filename}.pdf")

        with open(pdf_path, 'wb') as f:
            f.write(pdf_response.content)

        return True, pdf_path, "Downloaded successfully"

    except Exception as e:
        return False, None, f"Error: {str(e)}"

def download_papers_from_csv(csv_path='acl_selective.csv', output_dir='papers', delay=1):
    """
    Download all papers from a CSV file containing paper titles

    Args:
        csv_path: Path to CSV file with 'title' column
        output_dir: Directory to save PDFs
        delay: Delay between downloads in seconds
    """
    # Read CSV
    df = pd.read_csv(csv_path)

    if 'title' not in df.columns:
        print(f"Error: CSV must contain 'title' column")
        return

    print(f"Found {len(df)} papers to download from {csv_path}")
    print(f"Saving to: {output_dir}")
    print("-" * 80)

    # Track results
    results = []
    successful = 0
    failed = 0

    # Download each paper
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Downloading papers"):
        title = row['title']
        venue = row.get('venue', 'Unknown')

        success, pdf_path, message = search_and_download_acl_paper(title, output_dir)

        if success:
            successful += 1
            status = "✓"
        else:
            failed += 1
            status = "✗"

        results.append({
            'title': title,
            'venue': venue,
            'status': status,
            'pdf_path': pdf_path if success else None,
            'message': message
        })

        # Print progress
        tqdm.write(f"{status} [{idx+1}/{len(df)}] {title[:60]}... - {message}")

        # Delay to avoid overwhelming the server
        time.sleep(delay)

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_path = os.path.join(output_dir, 'download_results.csv')
    results_df.to_csv(results_path, index=False)

    # Print summary
    print("\n" + "=" * 80)
    print(f"Download Summary:")
    print(f"  Total papers: {len(df)}")
    print(f"  Successfully downloaded: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {successful/len(df)*100:.1f}%")
    print(f"\nResults saved to: {results_path}")
    print(f"PDFs saved to: {output_dir}")

def main():
    # Configuration
    csv_file = 'acl_selective.csv'
    output_directory = 'C:\\Users\\ZenBook\\Documents\\Reinforcement Learning LLMs\\ACL2025'
    delay_seconds = 2  # Delay between downloads

    # Check if CSV exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please run search_papers.py first to generate the CSV file.")
        return

    # Download papers
    download_papers_from_csv(csv_file, output_directory, delay_seconds)

if __name__ == "__main__":
    main()
