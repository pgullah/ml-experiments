

from datetime import datetime
from email.mime import message
import logging
from urllib import response
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.common.config import AppSettings
from app.planner import TravelPlanner
from app.agent import Agent
    

# @logging(level=logging.DEBUG)
def chat(thread_id: str | None = None):
    thread_id = thread_id or f"thread-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    settings = AppSettings()

    # Initialize Travel_Planner_Tools and Agent
    planner = TravelPlanner(settings)
    agent_instance = Agent(planner=planner)

    # Invoke the LangGraph agent with memory saver for chat
    logger.info("Starting agent in chat mode..")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            logger.info("Exiting chat.")
            break
        loading_msg = "Agent is thinking..."
        print(loading_msg, end="", flush=True)
        response = agent_instance.chat(user_query, thread_id)   
        print("\r" + " " * len(loading_msg) + "\r", end="", flush=True)
        print(f"Agent: {response}")
        

if __name__ == "__main__":
    logger.setLevel(logging.ERROR)
    chat()
