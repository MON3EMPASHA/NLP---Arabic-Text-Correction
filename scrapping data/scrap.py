import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_article_links(base_url, max_links):
    """Get article links from multiple pages with pagination support"""
    links = []
    page = 1
    base_section_url = 'https://www.youm7.com/Section/%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1-%D9%85%D8%B5%D8%B1%D9%8A%D8%A9/97'
    
    while len(links) < max_links:
        try:
            # Construct the page URL correctly
            if page == 1:
                current_url = f"{base_section_url}/1"
            else:
                current_url = f"{base_section_url}/{page}"
            
            print(f"Scraping page {page}: {current_url}")
            
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target both big article sections and regular articles
            article_containers = soup.find_all('div', class_=['bigOneSec', 'smallOneSec'])
            
            # Extract links from current page
            page_links = []
            for container in article_containers:
                link_tag = container.find('a', href=True)
                if link_tag and '/story/' in link_tag['href']:
                    full_url = urljoin(base_url, link_tag['href'])
                    if full_url not in links and full_url not in page_links:
                        page_links.append(full_url)
            
            # If no new links found, stop pagination
            if not page_links:
                print("No more articles found")
                break
            
            # Add new links to our collection
            links.extend(page_links)
            print(f"Found {len(page_links)} articles on this page (Total: {len(links)})")
            
            # Check if we've reached our limit
            if len(links) >= max_links:
                links = links[:max_links]  # Trim to exact max_links
                break
            
            # Move to next page
            page += 1
            
            # Be polite with delay between page requests
            time.sleep(2)
        
        except requests.exceptions.RequestException as e:
            print(f"Error requesting page {page}: {e}")
            break
        except Exception as e:
            print(f"Unexpected error on page {page}: {e}")
            break
    
    return links
def scrape_article(article_url):
    """Scrape individual article page for title and text with updated selectors"""
    try:
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('h1').text.strip() if soup.find('h1') else 'No title found'
        
        # Extract article text
        article_body = soup.find('div', {'id': 'articleBody'}) or soup.find('div', class_='articleCont')
        paragraphs = article_body.find_all('p') if article_body else []
        text = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        return {
            'title': title,
            'text': text,
            'url': article_url
        }
    
    except Exception as e:
        print(f"Error scraping article {article_url}: {e}")
        return None

def main():
    base_url = 'https://www.youm7.com/Section/%D8%AA%D9%82%D8%A7%D8%B1%D9%8A%D8%B1-%D9%85%D8%B5%D8%B1%D9%8A%D8%A9/97/1'
    max_links = 3000 
    
    print(f"Starting scrape of Youm7 articles from {base_url}")
    
    # Get article links with pagination
    article_links = get_article_links(base_url, max_links)
    print(f"\nTotal articles found: {len(article_links)}")
    
    # Scrape each article
    articles = []
    for link in article_links:
        article = scrape_article(link)
        if article:
            articles.append(article)
            print(f"Scraped: {article['title']}")
        time.sleep(1)  # Be polite with delay between requests
    
    # Save results as JSON
    if articles:
        output_file = 'clean_articles.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully saved {len(articles)} articles to {output_file}")
    else:
        print("No articles were scraped")

if __name__ == '__main__':
    main()