import asyncio
import os
import re
import json
from urllib.parse import urlparse
from pathlib import Path
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

def sanitize_filename(url):
    """Convert a URL to a valid filename."""
    # Parse the URL and get the path
    path = urlparse(url).path
    # Remove trailing slash if present
    if path.endswith('/'):
        path = path[:-1]
    # Use the path part or domain if path is empty
    if not path:
        path = urlparse(url).netloc
    
    # Remove any invalid filename characters and replace with underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', path)
    # Replace multiple consecutive underscores with a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # If empty after sanitization, use a default name
    if not sanitized:
        sanitized = "index"
        
    return f"{sanitized}.txt"

def extract_text_from_html(html_content, url):
    """Extract text content from HTML with improved handling for modern web pages."""
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script, style, and hidden elements
        for element in soup(["script", "style", "meta", "link", "noscript"]):
            element.extract()
            
        # For modern sites that use JavaScript frameworks (like Kaggle)
        # Look for structured data that might contain content
        json_ld_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_ld_data.append(json.loads(script.string))
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Try to find the main content area based on common patterns
        main_content = soup.find('main') or soup.find(id='content') or soup.find(class_='content')
        
        # Get specific content based on the URL/site type
        if 'kaggle.com' in url:
            # For Kaggle profiles, try to get profile information
            profile_sections = []
            
            # Try to find profile elements
            name_element = soup.find('h1') or soup.find(class_=lambda c: c and ('profile-name' in c or 'username' in c or 'displayName' in c))
            if name_element:
                profile_sections.append(f"Name: {name_element.get_text(strip=True)}")
            
            # Look for meta description which often contains profile summary
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                profile_sections.append(f"Bio: {meta_desc['content']}")
            
            # Extract any visible text that might be part of the profile
            profile_divs = soup.find_all('div', class_=lambda c: c and ('profile' in c or 'user-info' in c or 'bio' in c))
            for div in profile_divs:
                profile_sections.append(div.get_text(separator='\n', strip=True))
            
            # Specific Kaggle profile info like competitions, datasets, etc.
            sections = ['competitions', 'datasets', 'notebooks', 'discussion']
            for section in sections:
                section_element = soup.find(id=section) or soup.find(class_=lambda c: c and section in c)
                if section_element:
                    section_text = section_element.get_text(separator='\n', strip=True)
                    if section_text:
                        profile_sections.append(f"\n--- {section.upper()} ---\n{section_text}")
            
            if profile_sections:
                return '\n\n'.join(profile_sections)
        
        # If we found a main content area, use that
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Otherwise, get all text from the body
            body = soup.find('body')
            if body:
                text = body.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
        
        # Process the text to clean it up
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # If text is still very short, include any JSON-LD data we found
        if len(text) < 100 and json_ld_data:
            text += "\n\n--- STRUCTURED DATA ---\n"
            for item in json_ld_data:
                text += json.dumps(item, indent=2) + "\n"
        
        return text
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        # In case of error, try a simpler extraction
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            return soup.get_text(separator='\n', strip=True)
        except:
            return str(html_content)  # Return original content if all extraction fails

async def main():
    # Create output directory if it doesn't exist
    output_dir = Path("docs")
    output_debug_dir = Path("debug")
    output_dir.mkdir(exist_ok=True)
    output_debug_dir.mkdir(exist_ok=True)
    # Configure crawl parameters
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2, 
            include_external=False,  # Only crawl pages on the same domain
            max_pages=100  # Limit to prevent too many files
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    print(f"Starting crawler. Results will be saved to {output_dir}")
    
    # Track URLs we've seen to prevent duplicates
    processed_urls = set()
    
    async with AsyncWebCrawler() as crawler:
        # Set request delay for politeness
        crawler.request_delay = 0.5  # Be polite with delays between requests
        
        results = await crawler.arun("https://hcmut.edu.vn", config=config)

        print(f"Crawled {len(results)} pages in total")
        
        # Save results to text files
        for i, result in enumerate(results):
            url = result.url
            
            # Skip if we've already processed this URL
            if url in processed_urls:
                print(f"Skipping duplicate URL: {url}")
                continue
            
            processed_urls.add(url)
            
            # Generate a filename from the URL
            filename = sanitize_filename(url)
            # Add an index to make filenames unique if needed
            if os.path.exists(output_dir / filename):
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{i}{ext}"
            
            # Find the HTML content in one of the result attributes
            html_content = None
            if hasattr(result, 'html'):
                html_content = result.html
            elif hasattr(result, 'raw_html'):
                html_content = result.raw_html
            elif hasattr(result, 'data'):
                if isinstance(result.data, str):
                    html_content = result.data
                else:
                    html_content = str(result.data)
            elif result.metadata and 'html' in result.metadata:
                html_content = result.metadata['html']
            
            # For debugging, save the raw HTML to see what we're getting
            debug_path = output_debug_dir / f"debug_raw_{filename}"
            if html_content:
                try:
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(f"URL: {url}\n\n")
                        f.write(str(html_content)[:10000])  # Save first 10k chars for debugging
                except Exception as e:
                    print(f"Error saving debug content: {e}")
            
            # Extract text from HTML with site-specific handling
            if html_content:
                text_content = extract_text_from_html(html_content, url)
            else:
                # If no HTML content found, create simple text from metadata
                text_content = f"URL: {url}\n"
                for key, value in result.metadata.items():
                    if key not in ['html', 'raw_html']:  # Skip raw HTML in metadata
                        text_content += f"{key}: {value}\n"
                
            if not text_content or len(text_content.strip()) < 10:  # Check if content is too short
                print(f"Warning: Very little content found for {url} - only {len(text_content.strip())} chars")
                
                # Try to get any content we can
                text_content = f"URL: {url}\n\n"
                for key, value in vars(result).items():
                    if key.startswith('_') or key in ['url', 'metadata']:
                        continue
                    if isinstance(value, str) and len(value) > 0:
                        text_content += f"{key}: {value[:200]}...\n\n"  # First 200 chars of each attribute
                
                # Add metadata as a last resort
                text_content += "--- METADATA ---\n"
                for key, value in result.metadata.items():
                    if key not in ['html', 'raw_html']:
                        text_content += f"{key}: {value}\n"
                
            # Save content to file
            file_path = output_dir / filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Depth: {result.metadata.get('depth', 0)}\n")
                    title = result.metadata.get('title', 'No title')
                    f.write(f"Title: {title}\n\n")
                    f.write(text_content)
                print(f"Saved content for {url} to {file_path}")
            except Exception as e:
                print(f"Error saving content for {url}: {e}")
        
        print(f"Successfully saved {len(processed_urls)} unique pages to {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())