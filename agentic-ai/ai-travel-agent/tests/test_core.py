import unittest
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage

from app.agent import Agent
from app.guard.policy import DomainClassification, TRAVEL_REFUSAL
from app.planner import DayPlanInput
from app.prompt.prompt_loader import load_prompts
from app.tools.currency import CurrencyTool
from app.tools.search import GoogleSerperAPIWrapperTool, SearchTool
from app.tools.weather import WeatherTool


class FakePlanner:
    tools = []

    class TravelLLM:
        def __init__(self):
            self.invocations = 0

        def invoke(self, messages):
            self.invocations += 1
            return AIMessage(content="ok")

    class DomainLLM:
        def __init__(self, classification):
            self.classification = classification

        def with_structured_output(self, schema):
            return self

        def invoke(self, messages):
            return self.classification

    def __init__(self, decision="in_scope", confidence=1.0):
        classification = DomainClassification(
            decision=decision,
            confidence=confidence,
            reason="test classification",
        )
        self.llm = self.DomainLLM(classification)
        self.llm_with_tools = self.TravelLLM()


class CoreTests(unittest.TestCase):
    def test_agent_checkpoints_are_not_shared(self):
        first = Agent(FakePlanner())
        second = Agent(FakePlanner())
        self.assertIsNot(first.checkpointer, second.checkpointer)
        self.assertEqual(first.chat("hello", "thread-1"), "ok")

    def test_agent_chat_allows_in_scope_request(self):
        planner = FakePlanner(decision="in_scope", confidence=0.95)
        agent = Agent(planner)

        result = agent.chat("Plan a weekend in Paris", "travel-thread")

        self.assertEqual(result, "ok")
        self.assertEqual(planner.llm_with_tools.invocations, 1)

    def test_agent_chat_rejects_out_of_scope_request(self):
        planner = FakePlanner(decision="out_of_scope", confidence=0.99)
        agent = Agent(planner)

        result = agent.chat("Write a Python sorting algorithm", "blocked-thread")

        self.assertEqual(result, TRAVEL_REFUSAL)
        self.assertEqual(planner.llm_with_tools.invocations, 0)

    def test_agent_chat_rejects_low_confidence_request(self):
        planner = FakePlanner(decision="in_scope", confidence=0.79)
        agent = Agent(planner)

        result = agent.chat("Tell me about Paris", "uncertain-thread")

        self.assertEqual(result, TRAVEL_REFUSAL)
        self.assertEqual(planner.llm_with_tools.invocations, 0)

    def test_search_result_normalization(self):
        self.assertEqual(SearchTool._format_results("plain result"), "plain result")
        result = SearchTool._format_results(
            [{"url": "https://example.com", "content": "Example"}]
        )
        self.assertIn("https://example.com", result)
        self.assertIn("Example", result)

    @patch("app.tools.search.GoogleSerperAPIWrapper.run", return_value="search result")
    def test_google_serper_tool_initializes_and_invokes(self, run):
        tool = GoogleSerperAPIWrapperTool(serper_api_key="test-key")

        self.assertEqual(tool.invoke("hotels in London"), "search result")
        run.assert_called_once_with("hotels in London")

    def test_day_plan_nested_items_are_validated(self):
        plan = DayPlanInput(
            date="2026-01-01",
            day_number=1,
            plan_items=[{"time": "09:00", "activity": "Walk", "estimated_cost": "£10"}],
        )
        self.assertEqual(plan.plan_items[0].estimated_cost, "£10")

    def test_prompt_loader_accepts_plain_markdown(self):
        prompts = load_prompts()
        self.assertTrue(prompts)
        self.assertTrue(all(prompt["prompt"] for prompt in prompts))

    @patch("app.tools.currency.requests.get")
    def test_currency_uses_timeout_and_normalized_codes(self, get):
        response = Mock()
        response.json.return_value = {"rates": {"JPY": 200.0}}
        get.return_value = response
        self.assertEqual(CurrencyTool().convert_currency(1, "gbp", "jpy"), 200.0)
        _, kwargs = get.call_args
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["params"]["to"], "JPY")

    @patch("app.tools.weather.requests.get")
    def test_forecast_caps_openweather_window(self, get):
        response = Mock()
        response.json.return_value = {"list": []}
        get.return_value = response
        config = Mock()
        config.weather_api.return_value = Mock(api_key="key", api_url="https://weather/")
        WeatherTool(config).get_forecast("Tokyo", 20)
        self.assertEqual(get.call_args.kwargs["params"]["cnt"], 40)
        self.assertEqual(get.call_args.kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
