import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    """Clean text by removing extra whitespace and special characters"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def get_web_info(query, max_results=3):
    """Get clean information from the web about a query"""
    try:
        # Use DuckDuckGo for search
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        results = []
        for result in soup.select('.result__body')[:max_results]:
            title = result.select_one('.result__title')
            snippet = result.select_one('.result__snippet')
            
            if title and snippet:
                results.append({
                    'title': clean_text(title.get_text()),
                    'info': clean_text(snippet.get_text())
                })
        
        return results
    except Exception as e:
        return [{'title': 'Error', 'info': f'Failed to get web info: {str(e)}'}]

def summarize_web_results(results):
    """Format web results into a clean, readable string"""
    if not results:
        return "No information found."
        
    summary = []
    for result in results:
        summary.append(f"{result['info']}")
    
    return "\n\n".join(summary)
