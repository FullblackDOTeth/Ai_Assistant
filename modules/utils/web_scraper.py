"""
Web scraping utilities for Head AI
Handles web requests and HTML parsing
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, timeout: int = 10):
        """Initialize WebScraper with custom timeout"""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HeadAI Research Bot/1.0'
        })

    def get_page(self, url: str) -> Optional[str]:
        """
        Fetch webpage content safely
        
        Args:
            url: The URL to fetch
            
        Returns:
            str: HTML content if successful, None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None

    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content into BeautifulSoup object
        
        Args:
            html: HTML content to parse
            
        Returns:
            BeautifulSoup: Parsed HTML if successful, None if failed
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return None

    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            str: Cleaned text content
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List[str]: List of absolute URLs
        """
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                if self._is_valid_url(absolute_url):
                    links.append(absolute_url)
        return links

    def scrape_page(self, url: str) -> Dict[str, Union[str, List[str], None]]:
        """
        Scrape a webpage and extract useful information
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict containing:
                - text: Extracted text content
                - links: List of links found
                - title: Page title
                - error: Error message if failed
        """
        result = {
            'text': None,
            'links': [],
            'title': None,
            'error': None
        }

        html = self.get_page(url)
        if not html:
            result['error'] = f"Failed to fetch {url}"
            return result

        soup = self.parse_html(html)
        if not soup:
            result['error'] = "Failed to parse HTML"
            return result

        result['text'] = self.extract_text(soup)
        result['links'] = self.extract_links(soup, url)
        result['title'] = soup.title.string if soup.title else None

        return result

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and uses http(s) protocol"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and parsed.scheme in ('http', 'https')
        except Exception:
            return False
