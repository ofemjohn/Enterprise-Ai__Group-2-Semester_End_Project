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
    
    @staticmethod
    def should_skip_url(url: str) -> bool:
        """
        Skip URLs that are likely filter/query pages that generate too many variations.
        This helps avoid crawling thousands of filter combination pages.
        """
        parsed = urlparse(url)
        query = parsed.query.lower()
        path = parsed.path.lower()
        
        # Skip URLs with filter parameters (color, size, display, etc.)
        filter_params = ['color=', 'size=', 'display=', 'filter=', 'sort=', 'page=']
        if any(param in query for param in filter_params):
            # Allow if it's a simple page parameter (like page=1, page=2)
            if 'page=' in query and len(query.split('&')) == 1:
                # Allow simple pagination
                pass
            else:
                # Skip complex filter combinations
                return True
        
        # Skip review/comment pages
        if '/newreview' in path or '/review' in path or '/comment' in path:
            return True
        
        # Skip cart/checkout/account pages for bookstore
        if any(skip in path for skip in ['/cart', '/checkout', '/account', '/login', '/register']):
            return True
        
        return False
    
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
        total_visited = len(self.visited)
        queue_size = len(self.queue)
        print(f"\n[{total_visited}] [Depth {depth}/{max_depth_for_branch}] Crawling: {normalized_url}", flush=True)
        
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
                print(f"  ✓ Extracted {len(downloaded):,} characters", flush=True)
            else:
                print(f"  ⚠ No text content extracted", flush=True)
            
            # Parse HTML and get all internal links
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                if href:
                    absolute_url = urljoin(normalized_url, href)
                    normalized_link = self.normalize_url(absolute_url)
                    
                    # Skip URLs that are filter/query pages
                    if self.should_skip_url(normalized_link):
                        continue
                    
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
            
            print(f"  → Found {len(unique_links)} new links to crawl (Queue: {len(self.queue)})", flush=True)
            return unique_links
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"  ✗ Error on {normalized_url}: {e}", flush=True)
            return []
        
        finally:
            if page:
                await page.close()
            
            # Rate limiting
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    def save_results(self, output_path: Path, append: bool = False):
        """Save results to JSONL file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = "a" if append else "w"
        with open(output_path, mode, encoding="utf-8") as f:
            for r in self.results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    async def crawl_entry_point(self, browser, start_url: str, allowed_domains: list, max_depth: int):
        """
        Crawl a single entry point completely before moving to the next.
        Returns the number of pages crawled.
        """
        # Track results count before starting
        results_count_before = len(self.results)
        
        # Reset state for this entry point (but keep global visited set)
        entry_visited = set()
        entry_queue = deque()
        
        normalized_start = self.normalize_url(start_url)
        entry_queue.append((normalized_start, 0))
        entry_visited.add(normalized_start)
        
        print(f"\n{'='*70}")
        print(f"Processing entry point: {start_url}")
        print(f"Max depth: {max_depth}, Allowed domains: {allowed_domains}")
        print(f"{'='*70}\n", flush=True)
        
        # Process this entry point's queue
        while entry_queue:
            url, depth = entry_queue.popleft()
            
            # Crawl the page (this will add to self.results)
            try:
                new_links = await self.crawl_page(browser, url, depth, allowed_domains, max_depth)
                
                # Add new links to queue if we haven't exceeded max depth
                if depth < max_depth:
                    for link in new_links:
                        # Skip filter/query URLs
                        if self.should_skip_url(link):
                            continue
                        
                        if link not in entry_visited and link not in self.visited:
                            entry_visited.add(link)
                            entry_queue.append((link, depth + 1))
                            
            except Exception as e:
                print(f"  ✗ Error processing {url}: {e}", flush=True)
                self.stats["errors"] += 1
        
        pages_crawled = len(self.results) - results_count_before
        print(f"\n  Entry point complete: {pages_crawled} pages crawled", flush=True)
        return pages_crawled
    
    async def run(self):
        """Main crawling function - processes each entry point sequentially."""
        print(f"Starting sequential crawl with {len(START_URLS)} entry points", flush=True)
        print(f"Global max depth: {MAX_DEPTH}", flush=True)
        print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests", flush=True)
        print(f"Results will be saved after each entry point\n", flush=True)
        
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear output file if it exists (start fresh)
        if output_path.exists():
            output_path.unlink()
        
        print("Initializing Playwright...", flush=True)
        
        async with async_playwright() as p:
            print("Launching Firefox browser...", flush=True)
            browser = await p.firefox.launch(headless=True)
            print("Browser launched successfully!\n", flush=True)
            
            try:
                # Process each entry point sequentially
                for idx, (start_url, allowed_domains, max_depth) in enumerate(START_URLS, 1):
                    print(f"\n{'#'*70}")
                    print(f"Entry Point {idx}/{len(START_URLS)}")
                    print(f"{'#'*70}", flush=True)
                    
                    try:
                        # Crawl this entry point
                        pages_crawled = await self.crawl_entry_point(browser, start_url, allowed_domains, max_depth)
                        
                        # Save results after each entry point
                        self.save_results(output_path, append=(idx > 1))
                        print(f"  ✓ Saved {len(self.results)} total pages so far to {output_path}", flush=True)
                        
                        # Clear results list to avoid memory issues (already saved)
                        # Keep visited set to avoid re-crawling across entry points
                        self.results = []
                        
                    except KeyboardInterrupt:
                        print("\n\nCrawling interrupted by user")
                        # Save what we have so far
                        if self.results:
                            self.save_results(output_path, append=True)
                        raise
                    except Exception as e:
                        print(f"\n  ✗ Error processing entry point {idx}: {e}", flush=True)
                        print(f"  Continuing with next entry point...\n", flush=True)
                        # Continue with next entry point
                        continue
                
                await browser.close()
                
            except KeyboardInterrupt:
                print("\n\nCrawling interrupted by user")
                # Save what we have so far
                if self.results:
                    self.save_results(output_path, append=True)
                await browser.close()
            except Exception as e:
                print(f"\n\nFatal error: {e}")
                # Save what we have so far
                if self.results:
                    self.save_results(output_path, append=True)
                await browser.close()
                raise
        
        # Final summary
        print("\n" + "="*60)
        print("CRAWLING SUMMARY")
        print("="*60)
        print(f"Total pages visited: {len(self.visited)}")
        print(f"Successfully extracted: {self.stats['success']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Results saved to: {output_path}")
        
        # Read back results for final count
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                total_lines = sum(1 for _ in f)
            print(f"Total records in file: {total_lines}")
        
        print("="*60)


async def main():
    """Entry point for the crawler."""
    crawler = WebCrawler()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())

