from typing import TypedDict
from langgraph.graph import StateGraph, START, END


def add_one(state):
    return {"number": state["number"] + 1}


def double(state):
    return {"number": state["number"] * 2}

class MyState(TypedDict):
    number: int


builder = StateGraph(MyState)

builder.add_node("add_one", add_one)
builder.add_node("double", double)

builder.add_edge(START, "add_one")
builder.add_edge("add_one", "double")
builder.add_edge("double", END)

graph = builder.compile()

result = graph.invoke({"number": 10})
print("lang graph result", result)