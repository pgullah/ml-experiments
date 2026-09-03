

from datetime import datetime

from app.common.config import ConfigProvider
from app.planner import TravelPlanner
from app.agent import Agent
    

def chat(thread_id: str | None = None):
    thread_id = thread_id or f"thread-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    configProvider = ConfigProvider()

    # Initialize Travel_Planner_Tools and Agent
    planner = TravelPlanner(configProvider)
    agent_instance = Agent(planner=planner)

    # Invoke the LangGraph agent with memory saver for chat
    print("Starting agent in chat mode..")
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Exiting chat.")
            break
        response = agent_instance.chat(user_query, thread_id)
        print("Agent says:")
        print(response)
        

if __name__ == "__main__":
    chat()