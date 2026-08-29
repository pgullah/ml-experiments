
from app.common.config import ConfigProvider
from app.planner import TravelPlanner
from app.agent import Agent

def main(user_query: str):
    configProvider = ConfigProvider()

    # Initialize Travel_Planner_Tools and Agent
    planner = TravelPlanner(configProvider)
    agent_instance = Agent(planner=planner)

    # Invoke the LangGraph agent
    # Initial input for LangGraph is a HumanMessage
    print("Starting agent..")
    response = agent_instance.chat(user_query)
    print("Agent says:")
    print(response)

if __name__ == "__main__":
    user_query="""
        Hey there! I'm planning a 7-day trip to Japan for next May. 
        My hotel budget is around £100 per night. I would like to know what the weather will be like, 
        what places I can visit, and how much the whole trip might cost. I'll be paying in Japanese Yen, 
        but my native currency is INR. Also, I prefer local food and public transportation. Can you plan it all for me?.
    """.lstrip()
    main(user_query)