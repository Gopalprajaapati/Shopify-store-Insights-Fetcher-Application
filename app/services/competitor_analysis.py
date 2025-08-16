import httpx
import asyncio
from typing import List
from bs4 import BeautifulSoup
import re
from app.utils.helpers import extract_domain

class CompetitorAnalyzer:
    def __init__(self, fetcher):
        self.fetcher = fetcher
        self.client = httpx.AsyncClient()
        
    async def find_competitors(self, max_results: int = 3) -> List[str]:
        """Find competitor websites by searching for similar stores"""
        try:
            search_query = f"similar sites to {extract_domain(self.fetcher.base_url)}"
            search_url = f"https://www.google.com/search?q={search_query}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = await self.client.get(search_url, headers=headers)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            competitor_links = []
            
            # Extract links from search results
            for result in soup.find_all('div', class_='tF2Cxc'):
                link = result.find('a')
                if link and link.get('href'):
                    url = link['href']
                    if url.startswith('/url?q='):
                        url = url[7:].split('&')[0]
                    if url not in competitor_links and url != self.fetcher.base_url:
                        competitor_links.append(url)
                        
            return competitor_links[:max_results]
        except Exception:
            return []