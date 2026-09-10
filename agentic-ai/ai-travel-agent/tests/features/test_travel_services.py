import logging
from unittest.mock import Mock

import pytest
import requests
from pydantic import SecretStr

from app.common.errors import SearchProviderError, ServiceError
from app.service.currency import CurrencyService
from app.service.search import (
    SearchProvider,
    SearchService,
    SerperSearchClient,
    TavilySearchClient,
)
from app.service.weather import WeatherService, WeatherTool
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
        monkeypatch.setattr("app.service.search.requests.post", post)
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

        assert result == [{"link": "https://example.com", "snippet": "Result"}]
        post.assert_called_once_with(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": "test-key",
                "Content-Type": "application/json",
            },
            json={"q": "hotels in London", "num": 5},
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
        monkeypatch.setattr("app.service.search.requests.post", post)
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

        assert result == [{"url": "https://example.com", "content": "Result"}]
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

    @pytest.mark.parametrize(
        ("client", "payload"),
        [
            (
                SerperSearchClient("key", "https://serper.test", 10),
                {"organic": "not-a-list"},
            ),
            (
                TavilySearchClient("key", "https://tavily.test", 10, 5),
                ["not-an-object"],
            ),
        ],
    )
    def test_search_clients_reject_malformed_provider_responses(
        self,
        monkeypatch,
        client,
        payload,
    ):
        response = Mock()
        response.json.return_value = payload
        monkeypatch.setattr(
            "app.service.search.requests.post", Mock(return_value=response)
        )

        with pytest.raises(SearchProviderError):
            client.search("Rome")

    def test_configured_search_providers_are_built_in_priority_order(self):
        settings = TEST_SETTINGS.model_copy(
            update={
                "serper_api_key": SecretStr("serper-secret"),
                "tavily_api_key": SecretStr("tavily-secret"),
            }
        )

        providers = SearchService._build_providers(settings)

        assert [provider.key for provider in providers] == [
            "serper",
            "tavily",
            "duckduckgo",
        ]
        assert "serper-secret" not in repr(providers[0].client)
        assert "tavily-secret" not in repr(providers[1].client)

    def test_search_falls_back_to_next_provider(self):
        unavailable = Mock()
        unavailable.search.side_effect = SearchProviderError("provider unavailable")
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

    def test_search_falls_back_when_results_have_no_usable_content(self):
        empty = Mock()
        empty.search.return_value = [{"unknown": "value"}]
        available = Mock()
        available.search.return_value = [{"body": "Useful result"}]
        search = SearchService(
            TEST_SETTINGS,
            providers=[
                SearchProvider("empty", 1, empty),
                SearchProvider("available", 2, available),
            ],
        )

        assert "Useful result" in search.run("hotels in London")
        available.search.assert_called_once()

    def test_search_output_and_result_count_are_bounded(self):
        provider = Mock()
        provider.search.return_value = [
            {"body": "x" * 100},
            {"body": "second"},
        ]
        settings = TEST_SETTINGS.model_copy(
            update={"search_max_results": 1, "search_max_output_characters": 20}
        )
        search = SearchService(
            settings,
            providers=[SearchProvider("bounded", 1, provider)],
        )

        result = search.run("hotels")

        assert len(result) == 20
        assert "second" not in result

    def test_currency_conversion_normalizes_codes_and_obeys_timeout(self, monkeypatch):
        get = Mock()
        monkeypatch.setattr("app.service.currency.requests.get", get)
        response = Mock()
        response.json.return_value = {"rates": {"JPY": 200.0}}
        get.return_value = response

        result = CurrencyService(TEST_SETTINGS).convert_currency(1, "gbp", "jpy")

        assert result == 200.0
        assert get.call_args.kwargs["timeout"] == 10
        assert get.call_args.kwargs["params"]["to"] == "JPY"

    def test_currency_timeout_becomes_a_safe_service_error(self, monkeypatch):
        monkeypatch.setattr(
            "app.service.currency.requests.get",
            Mock(side_effect=requests.Timeout("provider timeout")),
        )

        with pytest.raises(ServiceError, match="currently unavailable"):
            CurrencyService(TEST_SETTINGS).convert_currency(1, "GBP", "EUR")

    def test_weather_forecast_is_limited_to_supported_window(self, monkeypatch):
        get = Mock()
        monkeypatch.setattr("app.service.weather.requests.get", get)
        response = Mock()
        response.json.return_value = {"list": []}
        get.return_value = response
        settings = TEST_SETTINGS.model_copy(
            update={"openweathermap_api_url": "https://weather/"}
        )

        WeatherTool(settings).get_forecast("Tokyo", 20)

        assert get.call_args.kwargs["params"]["cnt"] == 40
        assert get.call_args.kwargs["timeout"] == 10

    def test_weather_http_error_does_not_expose_api_key(
        self,
        monkeypatch,
        caplog,
    ):
        secret = "weather-secret-value"
        settings = TEST_SETTINGS.model_copy(
            update={"openweathermap_api_key": SecretStr(secret)}
        )
        response = requests.Response()
        response.status_code = 401
        response.reason = "Unauthorized"
        response.url = f"https://weather.test/weather?q=London&appid={secret}"
        request = requests.Request("GET", response.url).prepare()
        response.request = request
        get = Mock(return_value=response)
        monkeypatch.setattr("app.service.weather.requests.get", get)

        with (
            caplog.at_level(logging.ERROR, logger="app.service.weather"),
            pytest.raises(ServiceError, match="currently unavailable") as error,
        ):
            WeatherService(settings).get_weather("London")

        assert secret not in str(error.value)
        assert secret not in caplog.text

    def test_weather_tool_alias_remains_compatible(self):
        assert WeatherTool is WeatherService

    def test_weather_rejects_malformed_json_shape(self, monkeypatch):
        response = Mock()
        response.json.return_value = ["unexpected"]
        monkeypatch.setattr(
            "app.service.weather.requests.get",
            Mock(return_value=response),
        )

        with pytest.raises(ServiceError, match="currently unavailable"):
            WeatherService(TEST_SETTINGS).get_forecast("Rome", 3)
