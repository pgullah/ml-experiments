from typing import List, Dict, Optional, Any, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from app.prompt.prompt_loader import load_raw_prompt

from app.planner import TravelPlanner

class Agent:
    
    def __init__(self, planner: TravelPlanner):
        self.planner=planner
        self.llm_with_tools = self.planner.llm_with_tools
        self.system_prompt = SystemMessage(content=load_raw_prompt())
        self.agent_graph = self._build_agent_graph()
    
    def _build_agent_graph(self):
        '''
        Build the agent graph with the necessary nodes and edges.
        Returns:
            StateGraph: The compiled state graph for the agent.
        '''
        
        def call_llm(state: MessagesState):
            '''
            Function to process user messages and invoke the tools
            Args:
                state (MessagesState): The current state of the messages.
            Returns:
                dict: A dictionary containing the updated messages state.
            '''
            user_question = state['messages']
            input_question = [self.system_prompt] + user_question
            response = self.llm_with_tools.invoke(input_question)
            
            return {'messages':[response]}
        
        def route_tool(state: MessagesState):
            last_message = state['messages'][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return 'tools'
            return END
        
        
        builder = StateGraph(MessagesState)
        builder.add_node('LLM_Decision_Step', call_llm)
        builder.add_node('tools', ToolNode(self.planner.tools))
    
        builder.add_edge(START,'LLM_Decision_Step')
        builder.add_conditional_edges(
            'LLM_Decision_Step',
            route_tool,
            {
                'tools' : 'tools',
                END : END
            }
        )
        builder.add_edge('tools','LLM_Decision_Step')
        return builder.compile()
    
    def chat(self, query: str):
        response_state = self.agent_graph.invoke({'messages': [HumanMessage(content=query)]})
        # The final output is the content of the last message in the state
        return response_state['messages'][-1].content
    