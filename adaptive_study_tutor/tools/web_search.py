from typing import Dict, Any
from config import TAVILY_API_KEY


def search_tavily(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Performs supplementary web search using Tavily API if API key is provided.
    Returns dict with success status, search summary, and results.
    """
    if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
        return {
            "success": False,
            "summary": "Tavily API key not configured.",
            "results": []
        }

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results)
        
        results = response.get("results", [])
        snippets = [f"- {r.get('title')}: {r.get('content')}" for r in results]
        summary = "\n".join(snippets)
        
        return {
            "success": True,
            "summary": summary,
            "results": results
        }
    except Exception as e:
        print(f"Tavily search error: {e}")
        return {
            "success": False,
            "summary": f"Search unavailable: {str(e)}",
            "results": []
        }
