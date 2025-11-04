"""
KSU IT Department Web Crawler

This module implements a BFS-based web crawler for scraping KSU IT department
websites and resources. It uses Playwright for browser automation and Trafilatura
for text extraction.
"""

import asyncio
import json
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import trafilatura

try:
    from .url_config import START_URLS, MAX_DEPTH, RATE_LIMIT_DELAY, OUTPUT_FILE
except ImportError:
    # Fallback for direct execution
    from url_config import START_URLS, MAX_DEPTH, RATE_LIMIT_DELAY, OUTPUT_FILE


class WebCrawler:
    """Web crawler for KSU IT department websites."""
    
    def __init__(self):
        self.visited = set()
        self.results = []
        self.queue = deque()
        self.stats = {"success": 0, "errors": 0, "skipped": 0}
        self.url_domains = {}  # Maps normalized_url -> list of allowed domains
        self.url_max_depth = {}  # Maps normalized_url -> max depth for this URL branch
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL to avoid duplicate crawls (remove fragments, normalize trailing slashes)."""
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        return normalized
    
    async def crawl_page(
        self, 
        browser, 
        url: str, 
        depth: int = 0, 
        allowed_domains: list = None, 
        max_depth_for_branch: int = MAX_DEPTH
    ) -> list:
        """
        Crawl a single page and extract content.
        
        Args:
            browser: Playwright browser instance
            url: URL to crawl
            depth: Current depth level
            allowed_domains: List of allowed domains for this crawl branch
            max_depth_for_branch: Maximum depth for this crawl branch
            
        Returns:
            List of new URLs found on the page
        """
        normalized_url = self.normalize_url(url)
        
        if normalized_url in self.visited:
            self.stats["skipped"] += 1
            return []
        
        if depth > max_depth_for_branch:
            self.stats["skipped"] += 1
            return []
        
        # Check if URL is in allowed domains
        if allowed_domains:
            parsed = urlparse(normalized_url)
            url_domain = parsed.netloc
            if not any(allowed in url_domain for allowed in allowed_domains):
                self.stats["skipped"] += 1
                return []
        
        self.visited.add(normalized_url)
        print(f"[Depth {depth}/{max_depth_for_branch}] Crawling: {normalized_url}")
        
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
                self.results.append({
                    "url": normalized_url,
                    "depth": depth,
                    "text": downloaded.strip()
                })
                self.stats["success"] += 1
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
                    normalized_link = self.normalize_url(absolute_url)
                    
                    # Check if it's in allowed domains and not visited
                    if allowed_domains:
                        parsed_link = urlparse(normalized_link)
                        link_domain = parsed_link.netloc
                        if any(allowed in link_domain for allowed in allowed_domains) and normalized_link not in self.visited:
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
            self.stats["errors"] += 1
            print(f"  ✗ Error on {normalized_url}: {e}")
            return []
        
        finally:
            if page:
                await page.close()
            
            # Rate limiting
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    async def run(self):
        """Main crawling function using BFS approach."""
        print(f"Starting crawl with {len(START_URLS)} entry points", flush=True)
        print(f"Global max depth: {MAX_DEPTH}", flush=True)
        print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests\n", flush=True)
        
        print("Initializing Playwright...", flush=True)
        
        async with async_playwright() as p:
            print("Launching Firefox browser...", flush=True)
            browser = await p.firefox.launch(headless=True)
            print("Browser launched successfully!\n", flush=True)
            
            try:
                # Initialize queue with all starting URLs
                for start_url, allowed_domains, max_depth in START_URLS:
                    normalized_start = self.normalize_url(start_url)
                    self.queue.append((normalized_start, 0))
                    self.url_domains[normalized_start] = allowed_domains
                    self.url_max_depth[normalized_start] = max_depth
                    print(f"Added entry point: {normalized_start} (domains: {allowed_domains}, max_depth: {max_depth})")
                print()
                
                # Process queue
                while self.queue:
                    url, depth = self.queue.popleft()
                    
                    # Get allowed domains and max depth for this URL
                    allowed_domains = self.url_domains.get(url, None)
                    max_depth_for_branch = self.url_max_depth.get(url, MAX_DEPTH)
                    
                    # Crawl the page and get new links
                    new_links = await self.crawl_page(browser, url, depth, allowed_domains, max_depth_for_branch)
                    
                    # Add new links to queue if we haven't exceeded max depth
                    if depth < max_depth_for_branch:
                        for link in new_links:
                            if link not in self.visited:
                                self.queue.append((link, depth + 1))
                                # Inherit domains and max depth from parent
                                self.url_domains[link] = allowed_domains
                                self.url_max_depth[link] = max_depth_for_branch
                
                await browser.close()
                
            except KeyboardInterrupt:
                print("\n\nCrawling interrupted by user")
                await browser.close()
            except Exception as e:
                print(f"\n\nFatal error: {e}")
                await browser.close()
                raise
        
        # Save results
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        
        # Print summary
        print("\n" + "="*60)
        print("CRAWLING SUMMARY")
        print("="*60)
        print(f"Total pages visited: {len(self.visited)}")
        print(f"Successfully extracted: {self.stats['success']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Results saved to: {output_path}")
        print(f"Total text extracted: {sum(len(r['text']) for r in self.results):,} characters")
        print("="*60)


async def main():
    """Entry point for the crawler."""
    crawler = WebCrawler()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())

