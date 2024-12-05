from __future__ import print_function
import os
import re
import requests
import logging
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlparse
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Optional environment variable for the output directory
BASE_OUTPUT_DIR = os.getenv('BASE_OUTPUT_DIR', os.path.join(os.getcwd(), 'output'))
logging.debug(f"BASE_OUTPUT_DIR: {BASE_OUTPUT_DIR}")

def clean_text(text):
    """Clean up text by removing unwanted UI elements and formatting."""
    if not text:
        return ''
    # Remove social media related text
    text = re.sub(r'Copy link(?:Facebook|Email|Notes|More|\s)*', '', text)
    
    # Remove audio player text
    text = re.sub(r'Audio playback is not supported.*upgrade\.', '', text)
    
    # Remove current time/total time text
    text = re.sub(r'\d+:\d+:\d+Current time:.*?Total time:.*?\d+:\d+:\d+', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def should_skip_element(tag):
    """Determine if an element should be skipped in the conversion."""
    # Skip script and style tags
    if tag.name in ['script', 'style']:
        return True
    
    # Skip JSON-LD content
    if tag.get('type') == 'application/ld+json':
        return True
        
    # Skip social sharing buttons and UI elements
    classes = tag.get('class', [])
    if any(c in str(classes) for c in ['share-button', 'social-links', 'player-controls']):
        return True
        
    return False

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(should_skip_element):
        element.decompose()
    
    def process_tag(tag):
        if isinstance(tag, NavigableString):
            return clean_text(tag.string) if tag.string else ''
        
        if should_skip_element(tag):
            return ''
        
        if tag.name == 'a':
            href = tag.get('href', '')
            # Skip processing if href contains javascript: or void(0)
            if 'javascript:' in href or 'void(0)' in href:
                return ''
                
            # Check if the link contains an image
            img = tag.find('img')
            if img:
                src = img.get('src', '')
                alt = img.get('alt', '')
                # Create a linked image in Markdown
                return f"[![{alt}]({src})]({href})"
            else:
                content = ''.join(process_tag(child) for child in tag.contents)
                return f"[{content}]({href})" if href else content
        elif tag.name == 'img':
            src = tag.get('src', '')
            alt = tag.get('alt', '')
            return f"![{alt}]({src})"
        elif tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag.name[1])
            content = ''.join(process_tag(child) for child in tag.contents)
            return f"\n\n{'#' * level} {clean_text(content)}\n\n"
        elif tag.name == 'p':
            content = ''.join(process_tag(child) for child in tag.contents)
            cleaned_content = clean_text(content)
            return f"\n\n{cleaned_content}\n\n" if cleaned_content else ''
        elif tag.name in ['ul', 'ol']:
            items = []
            for i, li in enumerate(tag.find_all('li', recursive=False)):
                marker = '*' if tag.name == 'ul' else f"{i+1}."
                content = ''.join(process_tag(child) for child in li.contents)
                cleaned_content = clean_text(content)
                if cleaned_content:
                    items.append(f"{marker} {cleaned_content}")
            return '\n' + '\n'.join(items) + '\n' if items else ''
        elif tag.name == 'br':
            return '\n'
        else:
            return ''.join(process_tag(child) for child in tag.contents)

    markdown_content = process_tag(soup.body or soup)
    
    # Clean up extra whitespace
    markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
    markdown_content = markdown_content.strip()

    return markdown_content

def download_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').split(';')[0].lower()

        if 'text/html' in content_type:
            return response.text
        else:
            logging.error(f"Unsupported content-type: {content_type}")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to download content from {url}: {e}")
        return None

def save_markdown(content, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def url_to_markdown(url):
    html_content = download_content(url)
    if html_content:
        markdown_content = html_to_markdown(html_content)
        return markdown_content
    return None

def get_output_filename(url, output_dir):
    """Determine the output filename based on the URL."""
    url_parts = urlparse(url)
    path_parts = url_parts.path.strip('/').split('/')
    
    # If the path ends with a specific identifier (not 'index'), use that
    if path_parts and path_parts[-1] != 'index':
        filename = f"{path_parts[-1]}.md"
    else:
        filename = 'index.md'
    
    return os.path.join(output_dir, filename)

def main(url):
    url_parts = urlparse(url)
    domain = url_parts.netloc
    date_dir = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(BASE_OUTPUT_DIR, date_dir, domain)

    markdown_content = url_to_markdown(url)
    if markdown_content:
        filename = get_output_filename(url, output_dir)
        save_markdown(markdown_content, filename)
        print(f"Markdown saved to: {filename}")
    else:
        print("Failed to convert the URL to Markdown.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python web2md.py <URL>")
        sys.exit(1)

    input_url = sys.argv[1]
    main(input_url)