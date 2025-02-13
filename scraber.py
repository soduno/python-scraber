import requests
from bs4 import BeautifulSoup
import os
import subprocess
import sys

link_starts_with = "#fillme";
link_ext = "#fillme";
content_selector = "#fillme";
next_page_selector = "#fillme"

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {url}", e)
        return None

def extract_links(html, selector, attribute='href'):
    soup = BeautifulSoup(html, 'html.parser')
    return [element.get(attribute) for element in soup.select(selector) if element.get(attribute)]

def execute_link(link):
    if link.startswith(link_starts_with):
        try:
            subprocess.run(["xdg-open" if sys.platform.startswith("linux") else "start", link], check=True)
            print(f"link executed: {link}")
        except subprocess.CalledProcessError as e:
            print("Error executing link:", e)
    elif link.endswith(link_ext):
        download_and_execute(link)

def download_and_execute(url):
    file_name = os.path.basename(url)
    file_path = os.path.join(os.getcwd(), file_name)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"Downloaded: {file_name}")
        subprocess.run(["xdg-open" if sys.platform.startswith("linux") else "start", file_path], check=True)
        print(f"file executed: {file_path}")
    except requests.RequestException as e:
        print("Error downloading the file:", e)
    except subprocess.CalledProcessError as e:
        print("Error executing file:", e)

def scrape_page(url):
    html = fetch_html(url)
    if not html:
        return None
    
    links = extract_links(html, content_selector)
    
    for link in links:
        print(f"Processing link: {link}")
        page_html = fetch_html(link)
        if not page_html:
            continue
        
        found_links = extract_links(page_html, 'a[href^="'+ link_starts_with +'"]') + extract_links(page_html, 'a[href$="'+link_ext+'"]')
        
        for found_link in found_links:
            execute_link(found_link)
    
    next_page_links = extract_links(html, next_page_selector)
    return next_page_links[0] if next_page_links else None

def main():
    url = input("Enter the URL to scrape: ")
    max_pages = int(input("Enter the number of pages to scrape: "))
    
    current_page = 1
    next_page_url = url
    
    while current_page <= max_pages and next_page_url:
        print(f"Scraping page {current_page}: {next_page_url}")
        next_page_url = scrape_page(next_page_url)
        current_page += 1
    
    print("Scraping complete.")

if __name__ == "__main__":
    main()
