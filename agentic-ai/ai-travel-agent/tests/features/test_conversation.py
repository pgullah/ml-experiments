import logging
from unittest.mock import Mock

import pytest
from langgraph.errors import GraphRecursionError

from app.agent import (
    AGENT_ERROR_RESPONSE,
    LLM_ERROR_RESPONSE,
    TOOL_LOOP_RESPONSE,
    Agent,
)
from tests.support.fakes import TEST_SETTINGS, FakePlanner


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

    def test_messages_sent_to_llm_are_bounded(self):
        planner = FakePlanner()
        planner.settings = TEST_SETTINGS.model_copy(
            update={"max_conversation_messages": 2}
        )
        agent = Agent(planner)

        agent.chat("Plan Rome", "thread")
        agent.chat("Make it cheaper", "thread")

        # One system prompt plus at most two retained conversation messages.
        assert len(planner.llm_with_tools.received_messages[-1]) <= 3
        state = agent._agent_graph.get_state({"configurable": {"thread_id": "thread"}})
        assert len(state.values["messages"]) <= 3

    def test_graph_recursion_limit_has_a_specific_safe_response(self):
        agent = Agent(FakePlanner())
        agent._agent_graph.invoke = Mock(side_effect=GraphRecursionError("loop"))

        assert agent.chat("Plan Rome", "thread") == TOOL_LOOP_RESPONSE

    def test_unexpected_graph_failure_has_a_safe_response(self):
        agent = Agent(FakePlanner())
        agent._agent_graph.invoke = Mock(side_effect=RuntimeError("internal detail"))

        result = agent.chat("Plan Rome", "thread")

        assert result == AGENT_ERROR_RESPONSE
        assert "internal detail" not in result

    @pytest.mark.parametrize("thread_id", ["", "   "])
    def test_blank_thread_id_is_rejected(self, thread_id):
        with pytest.raises(ValueError, match="thread_id"):
            Agent(FakePlanner()).chat("Plan Rome", thread_id)

    def test_oversized_query_is_rejected(self):
        planner = FakePlanner()
        planner.settings = TEST_SETTINGS.model_copy(
            update={"max_request_characters": 5}
        )

        with pytest.raises(ValueError, match="must not exceed"):
            Agent(planner).chat("Plan a long trip", "thread")

        assert planner.llm.invocations == []

    def test_blank_query_is_rejected_before_classification(self):
        planner = FakePlanner()

        with pytest.raises(ValueError, match="query must not be empty"):
            Agent(planner).chat("   ", "thread")

        assert planner.llm.invocations == []
