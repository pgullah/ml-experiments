import logging
from unittest.mock import Mock

from app.agent import Agent
from app.guard_rails.policy import TRAVEL_REFUSAL, travel_domain_guard
from tests.support.fakes import TEST_SETTINGS, FakePlanner


class TestTravelDomainEnforcement:
    def test_application_threshold_is_used_when_method_has_no_override(self):
        planner = FakePlanner(decision="in_scope", confidence=0.9)
        planner.settings = TEST_SETTINGS.model_copy(
            update={"domain_confidence_threshold": 0.95}
        )

        assert Agent(planner).chat("Plan a trip", "strict-thread") == TRAVEL_REFUSAL

    def test_method_threshold_overrides_application_default(self):
        planner = FakePlanner(decision="in_scope", confidence=0.9)

        class GuardedService:
            settings = TEST_SETTINGS.model_copy(
                update={"domain_confidence_threshold": 0.95}
            )
            llm = planner.llm

            @travel_domain_guard(confidence_threshold=0.85)
            def answer(self, query: str):
                return "allowed"

        assert GuardedService().answer("Plan a trip") == "allowed"

    def test_non_travel_request_is_refused_without_calling_travel_llm(self):
        planner = FakePlanner(decision="out_of_scope", confidence=0.99)

        result = Agent(planner).chat(
            "Write a Python sorting algorithm",
            "blocked-thread",
        )

        assert result == TRAVEL_REFUSAL
        assert planner.llm_with_tools.invocations == 0

    def test_low_confidence_request_is_refused(self):
        planner = FakePlanner(decision="in_scope", confidence=0.79)

        result = Agent(planner).chat("Tell me about Paris", "uncertain-thread")

        assert result == TRAVEL_REFUSAL
        assert planner.llm_with_tools.invocations == 0

    def test_travel_follow_up_is_classified_with_recent_context(self):
        planner = FakePlanner()
        agent = Agent(planner)

        agent.chat("Plan three days in Rome", "rome-thread")
        agent.chat("Can you make day two cheaper?", "rome-thread")

        classifier_message = planner.llm.invocations[1][-1].content
        assert "Plan three days in Rome" in classifier_message
        assert "assistant: ok" in classifier_message
        assert "Can you make day two cheaper?" in classifier_message

    def test_guard_context_is_bounded_per_thread_and_thread_count(self):
        planner = FakePlanner()
        planner.settings = TEST_SETTINGS.model_copy(
            update={"max_context_messages": 2, "max_guard_threads": 1}
        )
        agent = Agent(planner)

        agent.chat("Plan Rome", "rome")
        agent.chat("Plan Paris", "paris")

        assert list(agent._domain_context_by_thread) == ["paris"]
        assert len(agent._domain_context_by_thread["paris"]) == 2

    def test_classifier_failure_fails_closed(self, caplog):
        planner = FakePlanner()
        planner.llm.with_structured_output = Mock(
            side_effect=RuntimeError("guard unavailable")
        )

        with caplog.at_level(logging.ERROR, logger="app.guard_rails.policy"):
            result = Agent(planner).chat(
                "Write a Python program",
                "error-thread",
            )

        assert result == TRAVEL_REFUSAL
        assert planner.llm_with_tools.invocations == 0
        assert "Travel domain classification failed" in caplog.text
