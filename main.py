import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import trafilatura
import json
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque

BASE_DOMAIN = "campus.kennesaw.edu"
START_URL = "https://campus.kennesaw.edu/offices-services/uits/services/index.php"
MAX_DEPTH = 3
RATE_LIMIT_DELAY = 1.0  # seconds between requests

visited = set()
results = []
queue = deque()
stats = {"success": 0, "errors": 0, "skipped": 0}

def normalize_url(url):
    """Normalize URL to avoid duplicate crawls (remove fragments, normalize trailing slashes)"""
    parsed = urlparse(url)
    # Remove fragment and normalize path
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip('/') or '/',
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))
    return normalized

async def crawl_page(browser, url, depth=0):
    """Crawl a single page and extract content"""
    normalized_url = normalize_url(url)
    
    if normalized_url in visited:
        stats["skipped"] += 1
        return []
    
    if depth > MAX_DEPTH:
        stats["skipped"] += 1
        return []
    
    if BASE_DOMAIN not in normalized_url:
        stats["skipped"] += 1
        return []
    
    visited.add(normalized_url)
    print(f"[Depth {depth}] Crawling: {normalized_url}")

    page = None
    try:
        # Create a new page for each request to avoid navigation issues
        page = await browser.new_page()
        page.set_default_timeout(60000)
        
        # Add user agent to be polite
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (compatible; KSU-Crawler/1.0; +https://campus.kennesaw.edu)"
        })
        
        # Navigate and wait for network to be idle
        await page.goto(normalized_url, wait_until="networkidle", timeout=60000)
        
        # Small delay to ensure page is fully loaded
        await page.wait_for_timeout(1000)
        
        html = await page.content()

        # Extract clean text with Trafilatura
        downloaded = trafilatura.extract(html, include_links=True)
        if downloaded and downloaded.strip():
            results.append({
                "url": normalized_url,
                "depth": depth,
                "text": downloaded.strip()
            })
            stats["success"] += 1
            print(f"  ✓ Extracted {len(downloaded)} characters")
        else:
            print(f"  ⚠ No text content extracted")

        # Parse HTML and get all internal links
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if href:
                absolute_url = urljoin(normalized_url, href)
                normalized_link = normalize_url(absolute_url)
                
                # Check if it's an internal link
                if BASE_DOMAIN in normalized_link and normalized_link not in visited:
                    links.append(normalized_link)
        
        # Remove duplicates while preserving order
        seen_links = set()
        unique_links = []
        for link in links:
            if link not in seen_links:
                seen_links.add(link)
                unique_links.append(link)
        
        print(f"  → Found {len(unique_links)} new links to crawl")
        return unique_links

    except Exception as e:
        stats["errors"] += 1
        print(f"  ✗ Error on {normalized_url}: {e}")
        return []
    
    finally:
        if page:
            await page.close()
        
        # Rate limiting
        await asyncio.sleep(RATE_LIMIT_DELAY)

async def main():
    """Main crawling function using BFS approach"""
    print(f"Starting crawl of {BASE_DOMAIN}", flush=True)
    print(f"Starting URL: {START_URL}", flush=True)
    print(f"Max depth: {MAX_DEPTH}", flush=True)
    print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests\n", flush=True)
    
    print("Initializing Playwright...", flush=True)
    
    async with async_playwright() as p:
        print("Launching Firefox browser...", flush=True)
        browser = await p.firefox.launch(headless=True)
        print("Browser launched successfully!\n", flush=True)
        
        try:
            # Start with the initial URL
            queue.append((START_URL, 0))
            
            # Process queue
            while queue:
                url, depth = queue.popleft()
                
                # Crawl the page and get new links
                new_links = await crawl_page(browser, url, depth)
                
                # Add new links to queue if we haven't exceeded max depth
                if depth < MAX_DEPTH:
                    for link in new_links:
                        if link not in visited:
                            queue.append((link, depth + 1))
            
            await browser.close()
            
        except KeyboardInterrupt:
            print("\n\nCrawling interrupted by user")
            await browser.close()
        except Exception as e:
            print(f"\n\nFatal error: {e}")
            await browser.close()
            raise

    # Save results
    output_file = "kennesaw_uits.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # Print summary
    print("\n" + "="*60)
    print("CRAWLING SUMMARY")
    print("="*60)
    print(f"Total pages visited: {len(visited)}")
    print(f"Successfully extracted: {stats['success']}")
    print(f"Errors: {stats['errors']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Results saved to: {output_file}")
    print(f"Total text extracted: {sum(len(r['text']) for r in results):,} characters")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
