"""
Search plugin that provides enhanced search capabilities
"""

from . import Plugin
import wikipedia
from duckduckgo_search import ddg
from scholarly import scholarly
from typing import List, Dict, Any

class SearchPlugin(Plugin):
    def __init__(self):
        self._name = "search"
        self._description = "Enhanced search capabilities across multiple sources"
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    def initialize(self) -> None:
        """Initialize search APIs"""
        wikipedia.set_lang("en")
        print(f"Initialized {self.name} plugin")
    
    def execute(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute search across multiple sources"""
        results = []
        
        # Wikipedia search
        try:
            wiki_results = wikipedia.search(query, results=1)
            if wiki_results:
                page = wikipedia.page(wiki_results[0], auto_suggest=False)
                results.append({
                    'source': 'Wikipedia',
                    'title': page.title,
                    'content': page.summary,
                    'url': page.url
                })
        except Exception as e:
            print(f"Wikipedia error: {e}")
        
        # DuckDuckGo search
        try:
            ddg_results = ddg(query, max_results=3)
            for r in ddg_results:
                results.append({
                    'source': 'Web',
                    'title': r['title'],
                    'content': r['snippet'],
                    'url': r['link']
                })
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
        
        # Google Scholar search
        try:
            search_query = scholarly.search_pubs(query)
            for _ in range(2):  # Get top 2 papers
                try:
                    paper = next(search_query)
                    results.append({
                        'source': 'Google Scholar',
                        'title': paper.bib.get('title', ''),
                        'content': paper.bib.get('abstract', '')[:500],
                        'url': f"https://scholar.google.com/scholar?q={paper.bib.get('title', '')}"
                    })
                except StopIteration:
                    break
        except Exception as e:
            print(f"Scholar error: {e}")
        
        return results
