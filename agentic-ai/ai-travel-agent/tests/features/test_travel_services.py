from unittest.mock import Mock

from app.tools.currency import CurrencyService
from app.tools.search import (
    SearchProvider,
    SearchService,
    SerperSearchClient,
    TavilySearchClient,
)
from app.tools.weather import WeatherTool
from tests.support.fakes import TEST_SETTINGS


class TestTravelServices:
    def test_search_results_are_normalized_for_agent_consumption(self):
        assert SearchService._format_results("plain result") == "plain result"
        result = SearchService._format_results(
            [{"url": "https://example.com", "content": "Example"}]
        )

        assert "https://example.com" in result
        assert "Example" in result

    def test_duckduckgo_result_shape_is_normalized(self):
        result = SearchService._format_results(
            [{"href": "https://example.com", "body": "Travel result"}]
        )

        assert "https://example.com" in result
        assert "Travel result" in result

    def test_serper_client_uses_http_api_contract(self, monkeypatch):
        post = Mock()
        monkeypatch.setattr("app.tools.search.requests.post", post)
        response = Mock()
        response.json.return_value = {
            "organic": [{"link": "https://example.com", "snippet": "Result"}]
        }
        post.return_value = response
        client = SerperSearchClient(
            api_key="test-key",
            api_url="https://google.serper.dev/search",
            timeout=10,
        )

        result = client.search("hotels in London")

        assert result == [
            {"link": "https://example.com", "snippet": "Result"}
        ]
        post.assert_called_once_with(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": "test-key",
                "Content-Type": "application/json",
            },
            json={"q": "hotels in London"},
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()

    def test_search_provider_representations_do_not_expose_serper_key(self):
        client = SerperSearchClient(
            api_key="serper-secret",
            api_url="https://google.serper.dev/search",
            timeout=10,
        )
        provider = SearchProvider("serper", 1, client)

        assert "serper-secret" not in repr(client)
        assert "serper-secret" not in repr(provider)

    def test_tavily_client_uses_http_api_contract(self, monkeypatch):
        post = Mock()
        monkeypatch.setattr("app.tools.search.requests.post", post)
        response = Mock()
        response.json.return_value = {
            "results": [{"url": "https://example.com", "content": "Result"}]
        }
        post.return_value = response
        client = TavilySearchClient(
            api_key="test-key",
            api_url="https://api.tavily.com/search",
            timeout=10,
            max_results=5,
        )

        result = client.search("hotels in London")

        assert result == [
            {"url": "https://example.com", "content": "Result"}
        ]
        post.assert_called_once_with(
            "https://api.tavily.com/search",
            headers={"Authorization": "Bearer test-key"},
            json={"query": "hotels in London", "max_results": 5},
            timeout=10,
        )
        response.raise_for_status.assert_called_once_with()

    def test_tavily_client_representation_does_not_expose_key(self):
        client = TavilySearchClient(
            api_key="tavily-secret",
            api_url="https://api.tavily.com/search",
            timeout=10,
            max_results=5,
        )

        assert "tavily-secret" not in repr(client)

    def test_search_falls_back_to_next_provider(self):
        unavailable = Mock()
        unavailable.search.side_effect = RuntimeError("provider unavailable")
        available = Mock()
        available.search.return_value = [
            {"href": "https://example.com", "body": "Fallback result"}
        ]
        search = SearchService(
            TEST_SETTINGS,
            providers=[
                SearchProvider("primary", 1, unavailable),
                SearchProvider("fallback", 2, available),
            ],
        )

        result = search.run("hotels in London")

        assert "Fallback result" in result
        unavailable.search.assert_called_once_with("hotels in London")
        available.search.assert_called_once_with("hotels in London")

    def test_currency_conversion_normalizes_codes_and_obeys_timeout(self, monkeypatch):
        get = Mock()
        monkeypatch.setattr("app.tools.currency.requests.get", get)
        response = Mock()
        response.json.return_value = {"rates": {"JPY": 200.0}}
        get.return_value = response

        result = CurrencyService(TEST_SETTINGS).convert_currency(1, "gbp", "jpy")

        assert result == 200.0
        assert get.call_args.kwargs["timeout"] == 10
        assert get.call_args.kwargs["params"]["to"] == "JPY"

    def test_weather_forecast_is_limited_to_supported_window(self, monkeypatch):
        get = Mock()
        monkeypatch.setattr("app.tools.weather.requests.get", get)
        response = Mock()
        response.json.return_value = {"list": []}
        get.return_value = response
        settings = TEST_SETTINGS.model_copy(
            update={"openweathermap_api_url": "https://weather/"}
        )

        WeatherTool(settings).get_forecast("Tokyo", 20)

        assert get.call_args.kwargs["params"]["cnt"] == 40
        assert get.call_args.kwargs["timeout"] == 10
