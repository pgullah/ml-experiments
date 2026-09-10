import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

import requests
from ddgs import DDGS
from pydantic import BaseModel, ConfigDict

from app.common.config import AppSettings
from app.common.errors import SearchProviderError, ServiceError

logger = logging.getLogger(__name__)


# ducktyping interface for search clients
class SearchClient(Protocol):
    def search(self, query: str) -> list[dict[str, Any]]: ...


class SearchResult(BaseModel):
    """Provider-independent search result safe for tool consumption."""

    model_config = ConfigDict(frozen=True)

    title: str | None = None
    url: str | None = None
    content: str


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
    max_results: int = 5

    def search(self, query: str) -> list[dict[str, Any]]:
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": self.max_results},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Search response must be an object")
            results = payload.get("organic", [])
            if not isinstance(results, list):
                raise TypeError("Search results must be a list")
            return results[: self.max_results]
        except (requests.RequestException, ValueError, TypeError) as error:
            raise SearchProviderError("Serper search failed") from error


@dataclass(frozen=True)
class TavilySearchClient:
    api_key: str = field(repr=False)
    api_url: str
    timeout: float
    max_results: int

    def search(self, query: str) -> list[dict[str, Any]]:
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": query, "max_results": self.max_results},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Search response must be an object")
            results = payload.get("results", [])
            if not isinstance(results, list):
                raise TypeError("Search results must be a list")
            return results[: self.max_results]
        except (requests.RequestException, ValueError, TypeError) as error:
            raise SearchProviderError("Tavily search failed") from error


@dataclass(frozen=True)
class DuckDuckGoSearchClient:
    max_results: int

    def search(self, query: str) -> list[dict[str, Any]]:
        try:
            return list(DDGS().text(query, max_results=self.max_results))
        except Exception as error:
            # DDGS does not expose a stable provider-specific exception hierarchy.
            raise SearchProviderError("DuckDuckGo search failed") from error


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
        self._search_providers = sorted(
            configured_providers, key=lambda provider: provider.priority
        )
        self._max_results = settings.search_max_results
        self._max_output_characters = settings.search_max_output_characters

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
                        max_results=settings.search_max_results,
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
                formatted_results = self._format_results(
                    results,
                    max_results=self._max_results,
                    max_characters=self._max_output_characters,
                )
                if formatted_results.strip():
                    return formatted_results
            except SearchProviderError:
                logger.warning(
                    "Search provider failed; trying fallback (provider=%s)",
                    provider.key,
                )

        raise ServiceError("All search providers failed or returned no results")

    @staticmethod
    def _format_results(
        results: Any,
        max_results: int = 20,
        max_characters: int = 12_000,
    ) -> str:
        if isinstance(results, str):
            return results[:max_characters]
        if isinstance(results, dict):
            results = results.get("results", [results])
        if isinstance(results, list):
            normalized: list[SearchResult] = []
            for result in results[:max_results]:
                if isinstance(result, dict):
                    title = result.get("title")
                    url = result.get("url") or result.get("link") or result.get("href")
                    content = (
                        result.get("content")
                        or result.get("snippet")
                        or result.get("body")
                        or result.get("title")
                    )
                    if content:
                        normalized.append(
                            SearchResult(
                                title=str(title) if title else None,
                                url=(
                                    str(url)
                                    if url
                                    and str(url).startswith(("https://", "http://"))
                                    else None
                                ),
                                content=str(content),
                            )
                        )
                else:
                    normalized.append(SearchResult(content=str(result)))

            formatted = []
            for result in normalized:
                parts = [f"Title: {result.title}"] if result.title else []
                if result.url:
                    parts.append(f"Source: {result.url}")
                parts.append(f"Content: {result.content}")
                formatted.append("\n".join(parts))
            return "\n\n".join(formatted)[:max_characters]
        return (str(results) if results is not None else "")[:max_characters]
