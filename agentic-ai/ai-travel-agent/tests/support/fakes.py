from langchain_core.messages import AIMessage

from app.common.config import AppSettings
from app.guard_rails.policy import DomainClassification

TEST_SETTINGS = AppSettings(
    _env_file=None,
    openrouter_api_key="test-openrouter-key",
    openweathermap_api_key="test-weather-key",
)


class FakePlanner:
    class TravelLLM:
        def __init__(self):
            self.invocations = 0
            self.received_messages = []

        def invoke(self, messages):
            self.invocations += 1
            self.received_messages.append(messages)
            return AIMessage(content="ok")

    class DomainLLM:
        def __init__(self, classification):
            self.classification = classification
            self.invocations = []

        def with_structured_output(self, schema):
            return self

        def invoke(self, messages):
            self.invocations.append(messages)
            return self.classification

    def __init__(self, decision="in_scope", confidence=1.0):
        self.settings = TEST_SETTINGS
        classification = DomainClassification(
            decision=decision,
            confidence=confidence,
            reason="test classification",
        )
        self.llm = self.DomainLLM(classification)
        self.llm_with_tools = self.TravelLLM()
        self.tools = []
