import requests
import wikipedia
from duckduckgo_search import ddg
from scholarly import scholarly
from stackapi import StackAPI
import json
from datetime import datetime

class FreeAIProvider:
    def __init__(self):
        # Initialize APIs
        wikipedia.set_lang("en")
        self.stack_api = StackAPI('stackoverflow')
        self.knowledge_base = {}
        print("AI Provider initialized with enhanced research capabilities")
    
    def search_scholar(self, query, max_results=2):
        """Search Google Scholar for academic papers"""
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            for _ in range(max_results):
                try:
                    paper = next(search_query)
                    results.append({
                        'title': paper.bib.get('title', ''),
                        'content': paper.bib.get('abstract', '')[:500],
                        'source': 'Google Scholar',
                        'url': f"https://scholar.google.com/scholar?q={paper.bib.get('title', '')}"
                    })
                except StopIteration:
                    break
            return results
        except Exception as e:
            print(f"Scholar error: {e}")
            return []

    def search_stack_overflow(self, query, max_results=2):
        """Search Stack Overflow for technical information"""
        try:
            questions = self.stack_api.fetch('search/advanced', 
                                          min_score=5,  # Only good questions
                                          sort='votes',
                                          q=query)
            results = []
            for q in questions['items'][:max_results]:
                results.append({
                    'title': q['title'],
                    'content': f"Score: {q.get('score', 0)} - {q.get('excerpt', '')}",
                    'source': 'Stack Overflow',
                    'url': q['link']
                })
            return results
        except Exception as e:
            print(f"Stack Overflow error: {e}")
            return []

    def search_web(self, query):
        """Search multiple sources for comprehensive information"""
        print(f"Researching: {query}")
        results = []
        
        # Wikipedia search
        try:
            wiki_results = wikipedia.search(query, results=1)
            if wiki_results:
                try:
                    page = wikipedia.page(wiki_results[0], auto_suggest=False)
                    results.append({
                        'title': page.title,
                        'content': page.summary,
                        'source': 'Wikipedia',
                        'url': page.url
                    })
                    print("Found Wikipedia result")
                except:
                    print("Wikipedia page error")
        except Exception as e:
            print(f"Wikipedia error: {e}")
        
        # DuckDuckGo search
        try:
            ddg_results = ddg(query, max_results=3)
            if ddg_results:
                for r in ddg_results:
                    results.append({
                        'title': r['title'],
                        'content': r['snippet'],
                        'source': 'Web',
                        'url': r['link']
                    })
                print("Found web results")
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
        
        # Academic papers
        results.extend(self.search_scholar(query))
        
        # Technical information
        if any(tech_term in query.lower() for tech_term in ['code', 'programming', 'blockchain', 'crypto', 'algorithm']):
            results.extend(self.search_stack_overflow(query))
        
        # Store in knowledge base with timestamp
        self.knowledge_base[query] = {
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        return results

    def generate_response(self, prompt):
        """Generate comprehensive response using multiple sources"""
        print("Generating response...")
        try:
            results = self.search_web(prompt)
            
            if not results:
                return "I couldn't find any information about that. Could you try rephrasing your question?"
            
            # Format response
            response = ""
            
            # Group results by source
            sources = {}
            for r in results:
                if r['source'] not in sources:
                    sources[r['source']] = []
                sources[r['source']].append(r)
            
            # Add Wikipedia content first if available
            if 'Wikipedia' in sources:
                response += f"From Wikipedia:\n{sources['Wikipedia'][0]['content']}\n\n"
            
            # Add academic content
            if 'Google Scholar' in sources:
                response += "Recent Academic Research:\n"
                for paper in sources['Google Scholar']:
                    response += f"• {paper['title']}\n{paper['content']}\n\n"
            
            # Add Stack Overflow content for technical questions
            if 'Stack Overflow' in sources:
                response += "Technical Insights from Stack Overflow:\n"
                for post in sources['Stack Overflow']:
                    response += f"• {post['title']}\n{post['content']}\n\n"
            
            # Add web results
            if 'Web' in sources:
                response += "Additional Web Sources:\n"
                for result in sources['Web']:
                    response += f"• {result['content']}\n\n"
            
            # Add all sources
            response += "\nSources:\n"
            for result in results:
                response += f"• {result['source']}: {result['url']}\n"
            
            print("Response generated with comprehensive research")
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I had trouble researching that topic. Please try again."
