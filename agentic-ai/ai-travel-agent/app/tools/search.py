from dataclasses import dataclass

from app.common.exceptions import ServiceError
from app.common.utils import lazy_init
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool
from app.common.config import ConfigProvider
from pydantic import Field
from typing import Any

@dataclass(frozen=True)
class SearchProvider:
    key: str
    priority: int
    instance: BaseTool  # The search provider instance (e.g., GoogleSerperAPIWrapper, TavilySearchResults, DuckDuckGoSearchRun)
    

class GoogleSerperAPIWrapperTool(BaseTool):
    name: str = "google_serper_search"
    description: str = "Search the web for current travel information using Google Serper."
    api_wrapper: GoogleSerperAPIWrapper = Field(exclude=True)

    def __init__(self, serper_api_key: str, **kwargs: Any) -> None:
        wrapper = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
        super().__init__(api_wrapper=wrapper, **kwargs)

    def _run(self, query: str) -> str:
        return self.api_wrapper.run(query)


class SearchTool:

    def __init__(self, config: ConfigProvider):
        serper_api = config.serper_api()
        tavily_api = config.tavily_api()
        # Initializing search tools
        if serper_api.api_key:
            self._register_search_provider(SearchProvider('google', priority=1, instance=GoogleSerperAPIWrapperTool(serper_api_key=serper_api.api_key)))
        if tavily_api.api_key:
            self._register_search_provider(SearchProvider('tavily', priority=2, instance=TavilySearchResults(max_results=5, tavily_api_key=tavily_api.api_key)))
        self._register_search_provider(SearchProvider('duckduckgo', priority=3, instance=DuckDuckGoSearchRun()))
        

    def run(self, query: str):
        if len(self._search_providers) == 0:
            raise ServiceError("No search providers avaiable! ")

        return self._format_results(self._search(query))
    

    @staticmethod
    def _format_results(results: Any) -> str:
        if isinstance(results, str):
            return results
        if isinstance(results, dict):
            results = results.get("results", [results])
        if isinstance(results, list):
            formatted = []
            for result in results:
                if isinstance(result, dict):
                    url = result.get("url") or result.get("link")
                    content = result.get("content") or result.get("snippet") or result.get("title")
                    parts = [f"Source: {url}"] if url else []
                    if content:
                        parts.append(f"Content: {content}")
                    if parts:
                        formatted.append("\n".join(parts))
                else:
                    formatted.append(str(result))
            return "\n\n".join(formatted)
        return str(results) if results is not None else ""

    
    def _register_search_provider(self, search_provider: SearchProvider):
        if not isinstance(search_provider, SearchProvider) or not isinstance(search_provider.instance, BaseTool):
            raise ValueError("Invalid search provider!")
        
        self._search_providers: list[SearchProvider] = lazy_init(self, '_search_providers', lambda: [])
        try:
            self._search_providers.append(search_provider)
        except Exception as e:
            # ignore
            print(f"Unable to register {search_provider.key} provider. Cause: {str(e)}")
    
    def _search(self, query: str):
        self._prioritized_search_providers: list[SearchProvider] = lazy_init(self, '_prioritized_search_providers', lambda: sorted(self._search_providers, key=lambda x: x.priority))
        # print("Prioriized providers: ", prioritized_search_providers)
        for sp in self._prioritized_search_providers:
            try:
                return sp.instance.invoke(query)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"{sp.key} Search failed.. fallback to another provider", str(e))
                
        raise ServiceError("Unable to find any valid search providers to continue with the request")
