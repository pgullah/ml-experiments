

from datetime import datetime

from app.common.config import ConfigProvider
from app.planner import TravelPlanner
from app.agent import Agent

def one_off(user_query: str):
    configProvider = ConfigProvider()

    # Initialize Travel_Planner_Tools and Agent
    planner = TravelPlanner(configProvider)
    agent_instance = Agent(planner=planner)

    # Invoke the LangGraph agent
    # Initial input for LangGraph is a HumanMessage
    print("Starting agent..")
    response = agent_instance.answer(user_query)
    print("Agent says:")
    print(response)
    

def chat(thread_id: str = f"thread-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"):
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
    user_query="""
        Hey there! I'm planning a 7-day trip to Japan for next May. 
        My hotel budget is around £100 per night. I would like to know what the weather will be like, 
        what places I can visit, and how much the whole trip might cost. I'll be paying in Japanese Yen, 
        but my native currency is INR. Also, I prefer local food and public transportation. Can you plan it all for me?.
    """.lstrip()
    # one_off(user_query)
    chat()