import logging
from unittest.mock import Mock

from app.agent import LLM_ERROR_RESPONSE, Agent
from tests.support.fakes import FakePlanner


class TestConversation:
    def test_valid_travel_request_produces_a_response(self):
        planner = FakePlanner(decision="in_scope", confidence=0.95)

        result = Agent(planner).chat("Plan a weekend in Paris", "travel-thread")

        assert result == "ok"
        assert planner.llm_with_tools.invocations == 1

    def test_separate_agents_do_not_share_conversation_checkpoints(self):
        first = Agent(FakePlanner())
        second = Agent(FakePlanner())

        assert first.checkpointer is not second.checkpointer
        assert first.chat("Plan a trip", "thread-1") == "ok"

    def test_follow_up_receives_previous_turns_from_the_same_thread(self):
        planner = FakePlanner()
        agent = Agent(planner)

        agent.chat("Plan three days in Rome", "rome-thread")
        agent.chat("Make day two cheaper", "rome-thread")

        follow_up_context = [
            message.content for message in planner.llm_with_tools.received_messages[1]
        ]
        assert "Plan three days in Rome" in follow_up_context
        assert "Make day two cheaper" in follow_up_context

    def test_different_threads_do_not_share_conversation_history(self):
        planner = FakePlanner()
        agent = Agent(planner)

        agent.chat("Plan three days in Rome", "rome-thread")
        agent.chat("Plan a weekend in Paris", "paris-thread")

        paris_context = [
            message.content for message in planner.llm_with_tools.received_messages[1]
        ]
        assert "Plan three days in Rome" not in paris_context
        assert "Plan a weekend in Paris" in paris_context

    def test_llm_failure_returns_a_safe_response(self, caplog):
        planner = FakePlanner(decision="in_scope", confidence=0.95)
        planner.llm_with_tools.invoke = Mock(
            side_effect=RuntimeError("provider unavailable")
        )

        with caplog.at_level(logging.ERROR, logger="app.agent"):
            result = Agent(planner).chat(
                "Plan a weekend in Paris",
                "error-thread",
            )

        assert result == LLM_ERROR_RESPONSE
        assert "Travel agent LLM invocation failed" in caplog.text
        assert "llm_type=TravelLLM" in caplog.text
        assert "conversation_message_count=1" in caplog.text
        assert "provider unavailable" not in result
