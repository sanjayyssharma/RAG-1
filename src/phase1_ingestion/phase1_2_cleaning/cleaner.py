import os
import re

# Directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cleaned")

def setup_directories():
    if not os.path.exists(CLEANED_DATA_DIR):
        os.makedirs(CLEANED_DATA_DIR)
        print(f"Created directory: {CLEANED_DATA_DIR}")

def clean_markdown(content, filename):
    # 1. Extract Fund Name from the first line or filename
    fund_name = filename.replace('.md', '').replace('-', ' ').title()
    
    # Try to find the fund name in the first few lines to be more accurate
    lines = content.split('\n')
    for line in lines[:10]:
        if "Mutual Fund Performance" in line:
            fund_name = line.split('-')[0].strip()
            break
            
    # 2. Find start of useful content
    # The string usually contains "NAV:" followed by details like Expense ratio, then "### Return calculator"
    start_idx = content.find("NAV:")
    if start_idx == -1:
        start_idx = content.find("### Return calculator")
        
    if start_idx == -1:
        print(f"Warning: Start marker not found for {filename}. Keeping from beginning.")
        start_idx = 0
        
    # 3. Find end of useful content
    # The string usually ends around "Home>Mutual Funds" or "Contact Us"
    end_idx = content.find("Home>Mutual Funds>")
    if end_idx == -1:
        end_idx = content.find("Contact UsDownload the App")
        
    if end_idx == -1:
        print(f"Warning: End marker not found for {filename}. Keeping until end.")
        end_idx = len(content)
        
    # 4. Extract the core block
    core_content = content[start_idx:end_idx]
    
    # 5. Assemble final clean markdown
    cleaned = f"# {fund_name}\n\n"
    cleaned += core_content.strip()
    
    # 6. Some basic cleanup of multiple blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned

def run_cleaner():
    setup_directories()
    
    if not os.path.exists(RAW_DATA_DIR):
        print(f"Raw data directory not found: {RAW_DATA_DIR}")
        return
        
    for filename in os.listdir(RAW_DATA_DIR):
        if not filename.endswith('.md'):
            continue
            
        raw_filepath = os.path.join(RAW_DATA_DIR, filename)
        cleaned_filepath = os.path.join(CLEANED_DATA_DIR, filename)
        
        with open(raw_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        cleaned_content = clean_markdown(content, filename)
        
        with open(cleaned_filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        # Compare sizes
        orig_size = os.path.getsize(raw_filepath)
        new_size = os.path.getsize(cleaned_filepath)
        print(f"Cleaned {filename}: {orig_size} bytes -> {new_size} bytes")

if __name__ == "__main__":
    run_cleaner()
