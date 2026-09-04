from dataclasses import dataclass, field
import logging
from typing import Any, Protocol, Sequence
from ddgs import DDGS
import requests
from app.common.config import AppSettings
from app.common.exceptions import ServiceError

logger = logging.getLogger(__name__)

# ducktyping interface for search clients
class SearchClient(Protocol):
    def search(self, query: str) -> Any: ...


@dataclass(frozen=True)
class SearchProvider:
    key: str
    priority: int
    client: SearchClient


@dataclass(frozen=True)
class SerperSearchClient:
    api_key: str = field(repr=False)
    api_url: str
    timeout: float

    def search(self, query: str) -> list[dict[str, Any]]:
        response = requests.post(
            self.api_url,
            headers={
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
            },
            json={"q": query},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("organic", [])


@dataclass(frozen=True)
class TavilySearchClient:
    api_key: str = field(repr=False)
    api_url: str
    timeout: float
    max_results: int

    def search(self, query: str) -> list[dict[str, Any]]:
        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"query": query, "max_results": self.max_results},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("results", [])


@dataclass(frozen=True)
class DuckDuckGoSearchClient:
    max_results: int

    def search(self, query: str) -> list[dict[str, Any]]:
        return list(DDGS().text(query, max_results=self.max_results))


class SearchService:
    def __init__(
        self,
        settings: AppSettings,
        providers: Sequence[SearchProvider] | None = None,
    ):
        configured_providers = (
            list(providers)
            if providers is not None
            else self._build_providers(settings)
        )
        self._search_providers = sorted(configured_providers, key=lambda provider: provider.priority)

    @staticmethod
    def _build_providers(settings: AppSettings) -> list[SearchProvider]:
        providers: list[SearchProvider] = []
        if settings.serper_api_key:
            providers.append(
                SearchProvider(
                    key="serper",
                    priority=1,
                    client=SerperSearchClient(
                        api_key=settings.serper_api_key.get_secret_value(),
                        api_url=str(settings.serper_api_url),
                        timeout=settings.request_timeout_seconds,
                    ),
                )
            )
        if settings.tavily_api_key:
            providers.append(
                SearchProvider(
                    key="tavily",
                    priority=2,
                    client=TavilySearchClient(
                        api_key=settings.tavily_api_key.get_secret_value(),
                        api_url=str(settings.tavily_api_url),
                        timeout=settings.request_timeout_seconds,
                        max_results=settings.search_max_results,
                    ),
                )
            )
        providers.append(
            SearchProvider(
                key="duckduckgo",
                priority=3,
                client=DuckDuckGoSearchClient(
                    max_results=settings.search_max_results,
                ),
            )
        )
        return providers

    def run(self, query: str) -> str:
        if not query or not query.strip():
            raise ValueError("Search query must not be empty")
        if not self._search_providers:
            raise ServiceError("No search providers available")

        for provider in self._search_providers:
            try:
                results = provider.client.search(query)
                if results:
                    return self._format_results(results)
            except Exception:
                logger.exception(
                    "Search provider failed; trying fallback (provider=%s)",
                    provider.key,
                )

        raise ServiceError("All search providers failed or returned no results")

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
                    url = (
                        result.get("url")
                        or result.get("link")
                        or result.get("href")
                    )
                    content = (
                        result.get("content")
                        or result.get("snippet")
                        or result.get("body")
                        or result.get("title")
                    )
                    parts = [f"Source: {url}"] if url else []
                    if content:
                        parts.append(f"Content: {content}")
                    if parts:
                        formatted.append("\n".join(parts))
                else:
                    formatted.append(str(result))
            return "\n\n".join(formatted)
        return str(results) if results is not None else ""
