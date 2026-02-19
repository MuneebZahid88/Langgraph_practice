from typing import TypedDict
from langgraph.graph import StateGraph, END

# --- Define your agent state ---
class AgentState(TypedDict):
    name: str
    age: int
    final: str

# --- Define your nodes ---
def first_node(state: AgentState) -> AgentState:
    state["final"] = f"hey {state['name']}"
    return state

def second_node(state: AgentState) -> AgentState:
    state["final"] =state['final'] + f" {state['age']} years old node 2"
    return state

def third_node(state: AgentState) -> AgentState:
    state["final"] = state['final'] + " node 3"
    return state


graph = StateGraph(AgentState)

graph.add_node("firstNode", first_node)
graph.add_node("secondNode", second_node)
graph.add_node("thirdNode", third_node)


graph.set_entry_point("firstNode")

graph.add_edge("firstNode", "secondNode")
graph.add_edge("secondNode", "thirdNode")
graph.set_finish_point("thirdNode")

app = graph.compile()

result = app.invoke({"name": "bob", "age": 30})   # goes to secondNode
print(result['final'])
result = app.invoke({"name": "bobby", "age": 30}) # goes to thirdNode
print(result['final'])