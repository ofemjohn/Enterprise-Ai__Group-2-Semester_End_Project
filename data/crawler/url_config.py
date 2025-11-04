"""
URL Configuration for KSU IT Department Web Crawler

This module contains the configuration for all starting URLs and their crawling parameters.
Each entry defines: (start_url, allowed_domains_list, max_depth)
"""

# Configuration: Multiple starting URLs with their allowed domains
# Format: (start_url, allowed_domains_list, max_depth)
START_URLS = [
    # ServiceNow KB articles (depth 1, just the article itself)
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=fb80b1881b669a14857311b6b04bcb9f", ["kennesaw.service-now.com"], 1),
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=84a472dc1bece1147486c885604bcbf2", ["kennesaw.service-now.com"], 1),
    ("https://kennesaw.service-now.com/sp?id=kb_article&sys_id=0f4162b8976bea90c475f977f053af38", ["kennesaw.service-now.com"], 1),
    
    # Bookstore (will crawl from this entry point)
    ("https://bookstore.kennesaw.edu/day-one-access", ["bookstore.kennesaw.edu"], 3),
    
    # Campus KSU UITS pages (will crawl from these entry points)
    ("https://campus.kennesaw.edu/offices-services/uits/", ["campus.kennesaw.edu"], 3),
    ("https://campus.kennesaw.edu/offices-services/uits/technology-guides/get-technology.php", ["campus.kennesaw.edu"], 3),
    ("https://campus.kennesaw.edu/offices-services/uits/services/project-requests.php", ["campus.kennesaw.edu"], 3),
    
    # PDF documents (depth 0, just the PDF itself)
    ("https://campus.kennesaw.edu/offices-services/uits/docs/standards-procedures/email-usage-standard-procedure-09-2024.pdf", ["campus.kennesaw.edu"], 0),
    ("https://campus.kennesaw.edu/offices-services/uits/docs/standards-procedures/mass-electronic-mailing-standard-09-2024.pdf", ["campus.kennesaw.edu"], 0),
    ("https://soar.kennesaw.edu/bitstream/handle/11360/6692/student-handbook_2021-2022.pdf?sequence=1&isAllowed=y", ["soar.kennesaw.edu"], 0),
    
    # External domains (depth 1-2, limited crawling)
    ("https://www.usg.edu/information_technology_services/assets/information_technology_services/documents/USG_ITHB_AI_Guide_(Final).pdf", ["www.usg.edu"], 0),
    ("https://www.turnitin.com/help_pages/student_faq.asp?r=87.6295589277586", ["www.turnitin.com"], 2),
]

# Global crawler settings
MAX_DEPTH = 3  # Global max depth (individual URLs can override with their own max_depth)
RATE_LIMIT_DELAY = 1.0  # seconds between requests
OUTPUT_FILE = "data/raw/kennesaw_uits.jsonl"  # Output file path

