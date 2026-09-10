import logging
from dataclasses import dataclass

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import ToolNode

from app.common.config import AppSettings
from app.guard_rails.policy import travel_domain_guard
from app.planner import TravelPlanner
from app.prompt.prompt_loader import load_raw_prompt

logger = logging.getLogger(__name__)
LLM_ERROR_RESPONSE = (
    "I'm sorry, but I couldn't process your request right now. Please try again."
)
AGENT_ERROR_RESPONSE = "I'm sorry, but the travel service encountered an unexpected error. Please try again."
TOOL_LOOP_RESPONSE = (
    "I'm sorry, but I couldn't complete the plan within the allowed processing steps. "
    "Please make the request more specific and try again."
)


@dataclass
class AgentResponse:
    content: str
    thread_id: str


class Agent:
    def __init__(self, planner: TravelPlanner, checkpointer=None):
        self.planner = planner
        self.settings: AppSettings = planner.settings
        self.llm = self.planner.llm
        self.llm_with_tools = self.planner.llm_with_tools
        self._system_prompt = SystemMessage(
            content=load_raw_prompt(settings=self.settings)
        )
        # Create a memory saver to store the state of the conversation
        self.checkpointer = checkpointer or InMemorySaver()
        self._agent_graph = self._build_agent_graph()

    def _build_agent_graph(self):
        """
        Build the agent graph with the necessary nodes and edges.
        Returns:
            StateGraph: The compiled state graph for the agent.
        """

        def call_llm(state: MessagesState):
            """
            Function to process user messages and invoke the tools
            Args:
                state (MessagesState): The current state of the messages.
            Returns:
                dict: A dictionary containing the updated messages state.
            """
            user_question = trim_messages(
                state["messages"],
                max_tokens=self.settings.max_conversation_messages,
                token_counter=len,
                strategy="last",
                start_on="human",
            )
            input_question = [self._system_prompt] + user_question
            try:
                response = self.llm_with_tools.invoke(input_question)
            except Exception:
                logger.exception(
                    "Travel agent LLM invocation failed; returning fallback response "
                    "(llm_type=%s, conversation_message_count=%d)",
                    type(self.llm_with_tools).__name__,
                    len(user_question),
                )
                response = AIMessage(content=LLM_ERROR_RESPONSE)

            # Replace the checkpoint history as well as bounding the model input.
            return {
                "messages": [
                    RemoveMessage(id=REMOVE_ALL_MESSAGES),
                    *user_question,
                    response,
                ]
            }

        def route_tool(state: MessagesState):
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"
            return END

        builder = StateGraph(MessagesState)
        builder.add_node("LLM_Decision_Step", call_llm)
        builder.add_node("tools", ToolNode(self.planner.tools))

        builder.add_edge(START, "LLM_Decision_Step")
        builder.add_conditional_edges(
            "LLM_Decision_Step", route_tool, {"tools": "tools", END: END}
        )
        builder.add_edge("tools", "LLM_Decision_Step")
        return builder.compile(checkpointer=self.checkpointer)

    @travel_domain_guard()
    def chat(self, query: str, thread_id: str) -> AgentResponse:
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id must not be empty")

        config: RunnableConfig = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": self.settings.graph_recursion_limit,
        }
        # Invoke the agent graph with the initial query and the memory saver
        try:
            response_state = self._agent_graph.invoke(
                {"messages": [HumanMessage(content=query)]},
                config=config,
            )
        except GraphRecursionError:
            logger.warning("Travel agent reached its graph recursion limit")
            return AgentResponse(content=TOOL_LOOP_RESPONSE, thread_id=thread_id)
        except Exception:
            logger.exception("Travel agent graph execution failed")
            return AgentResponse(content=AGENT_ERROR_RESPONSE, thread_id=thread_id)
        # The final output is the content of the last message in the state
        return AgentResponse(
            content=response_state["messages"][-1].content, thread_id=thread_id
        )
