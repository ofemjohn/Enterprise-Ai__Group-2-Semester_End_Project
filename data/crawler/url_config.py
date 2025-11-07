"""
URL Configuration for KSU IT Department Web Crawler

This module contains the configuration for all starting URLs and their crawling parameters.
Each entry defines: (start_url, allowed_domains_list, max_depth)
"""

# Configuration: Multiple starting URLs with their allowed domains
# Format: (start_url, allowed_domains_list, max_depth)
# Processed sequentially, one entry point at a time
#
# Depth Strategy:
# - Depth 0: Single page/document (PDFs, specific articles)
# - Depth 1: Main page + direct links (for self-contained content)
# - Depth 2: Main page + service pages + detail pages (for comprehensive coverage)
# - Depth 3: Only for main UITS hub to get all services and their sub-pages
START_URLS = [
    # IT Department Website (PRIORITY - depth 2 for comprehensive coverage)
    # Captures: Main page → Programs → Courses → Admission requirements → Student resources → Faculty info
    # This is the core source for IT department academic information
    ("https://www.kennesaw.edu/ccse/academics/information-technology/index.php", ["www.kennesaw.edu"], 2),
    
    # ServiceNow KB articles (depth 1 - articles are self-contained, just get the article itself)
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=fb80b1881b669a14857311b6b04bcb9f", ["kennesaw.service-now.com"], 1),
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=84a472dc1bece1147486c885604bcbf2", ["kennesaw.service-now.com"], 1),
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=0f4162b8976bea90c475f977f053af38", ["kennesaw.service-now.com"], 1),
    
    # Bookstore Day One Access (depth 1 - just the main info page, no e-commerce filtering)
    ("https://bookstore.kennesaw.edu/day-one-access", ["bookstore.kennesaw.edu"], 1),
    
    # Main UITS Hub (depth 2 - gets main page, service categories, and individual service pages)
    # This captures: Main → Services → Individual Service Pages
    ("https://campus.kennesaw.edu/offices-services/uits/", ["campus.kennesaw.edu"], 2),
    
    # Technology Guides (depth 2 - gets guide listing + individual guide pages)
    ("https://campus.kennesaw.edu/offices-services/uits/technology-guides/get-technology.php", ["campus.kennesaw.edu"], 2),
    
    # Project Requests (depth 2 - gets main page + related info pages)
    ("https://campus.kennesaw.edu/offices-services/uits/services/project-requests.php", ["campus.kennesaw.edu"], 2),
    
    # PDF documents (depth 0 - just the PDF itself, no crawling)
    ("https://campus.kennesaw.edu/offices-services/uits/docs/standards-procedures/email-usage-standard-procedure-09-2024.pdf", ["campus.kennesaw.edu"], 0),
    ("https://campus.kennesaw.edu/offices-services/uits/docs/standards-procedures/mass-electronic-mailing-standard-09-2024.pdf", ["campus.kennesaw.edu"], 0),
    ("https://soar.kennesaw.edu/bitstream/handle/11360/6692/student-handbook_2021-2022.pdf?sequence=1&isAllowed=y", ["soar.kennesaw.edu"], 0),
    
    # External domains (depth 1 - limited scope, just get the main page and direct links)
    ("https://www.usg.edu/information_technology_services/assets/information_technology_services/documents/USG_ITHB_AI_Guide_(Final).pdf", ["www.usg.edu"], 0),
    ("https://www.turnitin.com/help_pages/student_faq.asp?r=87.6295589277586", ["www.turnitin.com"], 1),
]

# Global crawler settings
MAX_DEPTH = 2  # Default max depth (individual URLs can override with their own max_depth)
# Note: Most entry points use depth 2, which provides:
# - Main page (depth 0)
# - Service/guide listings (depth 1) 
# - Individual service/guide detail pages (depth 2)
# This captures the essential IT information without over-crawling
RATE_LIMIT_DELAY = 1.0  # seconds between requests
OUTPUT_FILE = "data/raw/kennesaw_uits.jsonl"  # Output file path

