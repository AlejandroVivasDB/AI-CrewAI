import os
import requests
import json
from crewai_tools import BaseTool, tool
from exa_py import Exa
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain.tools import BaseTool
import chardet
from chardet.universaldetector import UniversalDetector

load_dotenv()

class SearchAndContents(BaseTool):
    name: str = "Search and Contents Tool"
    description: str = (
        "Searches the web based on a search query for the latest results. Uses the Exa API. This also returns the contents of the search results."
    )

    def _run(self, search_query: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        search_results = exa.search_and_contents(
            query=search_query,
            use_autoprompt=True,
            text={"include_html_tags": False, "max_characters": 8000},
        )
        return search_results


class FindSimilar(BaseTool):
    name: str = "Find Similar Tool"
    description: str = (
        "Searches for similar articles to a given article using the Exa API. Takes in a URL of the article."
    )

    def _run(self, article_url: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        search_results = exa.find_similar(url=article_url)
        return search_results


class GetContents(BaseTool):
    name: str = "Get Contents Tool"
    description: str = (
        "Gets the contents of a specific article using the Exa API. Takes in the ID of the article."
    )
    
    def _run(self, article_ids: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        contents = exa.get_contents(article_ids)
        return contents

class SearchInternetNearCity(BaseTool):
    name: str = "Search Internet Tool"
    description: str = "Use this tool to search the internet for information. This tool returns 7 results from Google search engine."

    def _run(self, query: str, city: str, limit: int = 7) -> str:
        localized_query = f"{query} near {city}"
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": localized_query,
            "num": limit,
        })
        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['organic']
    
        string = []
        for result in results:
            string.append(f"{result['title']}\n{result['snippet']}\n{result['link']}\n\n")
      
        return f"Search results for '{query}' in {city}:\n\n" + "\n".join(string)


class SearchInternet(BaseTool):
    name: str = "Search Internet Tool"
    description: str = "Use this tool to search the internet for information. This tool returns 5 results from Google search engine."

    def _run(self, query: str, limit: int = 5) -> str:
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": limit,
        })
        headers = {
            'X-API-KEY': os.getenv("SERPER_API_KEY"),
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['organic']
    
        string = []
        for result in results:
            string.append(f"{result['title']}\n{result['snippet']}\n{result['link']}\n\n")
      
        return f"Search results for '{query}':\n\n" + "\n".join(string)


class SearchInstagram(BaseTool):
    name: str = "Search Instagram Tool"
    description: str = "Use this tool to search Instagram. This tool returns 5 results from Instagram pages."

    def _run(self, query: str, limit: int = 5) -> str:
        return SearchInternet()._run(f"site:instagram.com {query}", limit=limit)


class OpenPage(BaseTool):
    name: str = "Open Page Tool"
    description: str = "Use this tool to open a webpage and get the content."

    def _run(self, url: str) -> str:
        loader = WebBaseLoader(url)
        content = loader.load()

        # Detect the encoding using chardet
        detector = UniversalDetector()
        detector.feed(content)
        detector.close()
        encoding = detector.result['encoding']

        if encoding:
            content = content.decode(encoding)
        else:
            content = content.decode('utf-8')  # Default to utf-8 if encoding not detected

        return content
