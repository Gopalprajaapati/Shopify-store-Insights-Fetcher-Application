# shopify_insights_app/services/scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict
from config import settings # Import settings

class WebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': settings.DEFAULT_USER_AGENT # Use user agent from config
        }

    def _make_request(self, url: str) -> Optional[requests.Response]:
        try:
            response = self.session.get(url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT) # Use timeout from config
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_html(self, path: str = "") -> Optional[BeautifulSoup]:
        url = urljoin(self.base_url, path)
        response = self._make_request(url)
        if response:
            return BeautifulSoup(response.text, 'html.parser')
        return None

    def fetch_json(self, path: str = "") -> Optional[Dict]:
        url = urljoin(self.base_url, path)
        response = self._make_request(url)
        if response:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError: # Corrected exception name
                print(f"Could not decode JSON from {url}")
                return None
        return None