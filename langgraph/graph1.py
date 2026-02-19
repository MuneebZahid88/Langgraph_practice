from typing import TypedDict
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    message: str


def complementary_agent(state: AgentState) -> AgentState:
    """complementary agent"""
    state["message"] = "complement to " + state["message"]
    return state


graph = StateGraph(AgentState)

graph.add_node("complementing", complementary_agent)

graph.set_entry_point("complementing")
graph.set_finish_point("complementing")

app = graph.compile()

result = app.invoke({"message": "bob"})

print(result)
