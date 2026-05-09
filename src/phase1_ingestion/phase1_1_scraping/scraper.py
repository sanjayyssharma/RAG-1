import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Configuration
URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# Directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

def setup_directories():
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
        print(f"Created directory: {RAW_DATA_DIR}")

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'iframe']):
        tag.decompose()
        
    return str(soup)

def scrape_and_save():
    setup_directories()
    
    for url in URLS:
        print(f"Fetching: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            # Clean the HTML
            cleaned_html = clean_html(response.text)
            
            # Convert to Markdown
            markdown_content = md(cleaned_html, heading_style="ATX", strip=['a', 'img'])
            
            # Extract filename from URL
            filename = url.split('/')[-1] + ".md"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            print(f"Successfully saved to: {filepath}\n")
            
        except Exception as e:
            print(f"Failed to fetch {url}: {e}\n")

if __name__ == "__main__":
    scrape_and_save()
