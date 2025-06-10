# web_tools.py
# agentic_ai_framework/tools/web_tools.py
import requests
import json
import asyncio
from config import SERPER_API_KEY
from utils.logger import setup_logger
from tools import BaseTool
from pydantic import BaseModel, Field

logger = setup_logger(__name__)

class SearchArgs(BaseModel):
    query: str = Field(..., description="The search query string.")

async def serper_search_func(query: str) -> str:
    """Performs a web search using the Serper API and returns the top results."""
    if not SERPER_API_KEY:
        logger.error("SERPER_API_KEY is not set in config.py or environment.")
        return "Error: Web search tool not configured."

    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"q": query})

    try:
        await asyncio.sleep(1) # Simulate network delay
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        results = response.json()
        
        # Extract relevant snippets
        snippets = [item['snippet'] for item in results.get('organic', []) if 'snippet' in item]
        if snippets:
            return " ".join(snippets[:5]) # Return top 5 snippets
        return "No relevant search results found."
    except requests.exceptions.RequestException as e:
        logger.error(f"Serper API request failed: {e}")
        return f"Error performing web search: {e}"
    except Exception as e:
        logger.error(f"Error processing Serper API response: {e}")
        return f"Error processing search results: {e}"

WebSearchTool = BaseTool(
    name="serper_search",
    description="Performs a web search to find information on the internet. Useful for factual queries, latest news, and general knowledge.",
    func=serper_search_func,
    schema=SearchArgs.model_json_schema()
)