import logging
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.agent import Agent
from app.common.config import AppSettings
from app.planner import TravelPlanner


# @logging(level=logging.DEBUG)
def chat(thread_id: str | None = None):
    thread_id = thread_id or f"thread-{uuid4()}"
    settings = AppSettings()  # pyright: ignore[reportCallIssue]

    # Initialize Travel_Planner_Tools and Agent
    planner = TravelPlanner(settings)
    agent_instance = Agent(planner=planner)

    # Invoke the LangGraph agent with memory saver for chat
    logger.info("Starting agent in chat mode..")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ["exit", "quit"]:
            logger.info("Exiting chat.")
            break
        loading_msg = "Agent is thinking..."
        print(loading_msg, end="", flush=True)
        try:
            response = agent_instance.chat(user_query, thread_id)
        except ValueError as error:
            response = str(error)
        print("\r" + " " * len(loading_msg) + "\r", end="", flush=True)
        print(f"Agent: {response}")


if __name__ == "__main__":
    logger.setLevel(logging.ERROR)
    chat()
