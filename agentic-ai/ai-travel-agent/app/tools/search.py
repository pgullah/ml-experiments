from dataclasses import dataclass

from app.common.exceptions import ServiceError
from app.common.utils import lazy_init
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import  DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from app.common.config import ConfigProvider
from collections.abc import Callable
from typing import Any

@dataclass(frozen=True)
class SearchProvider:
    key: str
    priority: int
    instance: Any
    # func: Callable[..., Any]


class SearchTool:
    
    def __init__(self, config: ConfigProvider):
        api_keys = config.get_api_keys()
        # Initializing search tools
        self._register_search_provider(SearchProvider('duckduckgo', priority=2, instance=DuckDuckGoSearchRun()))
        self._register_search_provider(SearchProvider('google', priority=1, instance=GoogleSerperAPIWrapper(serper_api_key=api_keys.serper_api_key)))
        self._register_search_provider(SearchProvider('tavily', priority=3, instance=TavilySearchResults(max_results=5, tavily_api_key=api_keys.tavily_api_key)))
        
    
    def run(self, query: str):
        results = None
        if len(self._search_providers) == 0:
            raise ServiceError("No search providers avaiable! ")

        results = self._search(query)
        if results:
            results = "\n".join([f'Source: {r['url']}\nContent: {r['content']}' for r in results])
            
        return results
        
    
    def _register_search_provider(self, search_provider: SearchProvider):
        self._search_providers: list[SearchProvider] = lazy_init(self, '_search_providers', lambda: [])
        try:
            self._search_providers.append(search_provider)
        except Exception as e:
            # ignore
            print(f"Unable to register {search_provider.key} provider. Cause: {str(e)}")
    
    def _search(self, query: str):
        self._prioritized_search_providers: list[SearchProvider] = lazy_init(self, '_prioritized_search_providers', lambda: sorted(self._search_providers, key=lambda x: x.priority, reverse=True))
        # print("Prioriized providers: ", prioritized_search_providers)
        for sp in self._prioritized_search_providers:
            try:
                print(f">>>>> Using search provider: {sp.key}")
                return sp.instance.invoke(query)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"{sp.key} Search failed.. fallback to another provider", str(e))
                
        raise ServiceError("Unable to find any valid search providers to continue with the request")