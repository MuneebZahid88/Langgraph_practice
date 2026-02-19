from typing import TypedDict
from langgraph.graph import StateGraph, END

# --- Define your agent state ---
class AgentState(TypedDict):
    name: str
    age: int
    final: str

# --- Define your nodes ---
def first_node(state: AgentState) -> AgentState:
    state["final"] = f"hey {state['name']} is {state['age']} years old"
    return state

def second_node(state: AgentState) -> AgentState:
    state["final"] = state['final'] + " node 2"
    return state

def third_node(state: AgentState) -> AgentState:
    state["final"] = state['final'] + " node 3"
    return state

# --- Router function ---
def route(state: AgentState) -> str:
    if len(state["name"]) < 4:
        return "secondNode"
    else:
        return "thirdNode"

# --- Create Graph ---
graph = StateGraph(AgentState)

graph.add_node("firstNode", first_node)
graph.add_node("secondNode", second_node)
graph.add_node("thirdNode", third_node)

# Conditional branching from firstNode
graph.add_conditional_edges(
    "firstNode",
    route,
    {
        "secondNode": "secondNode",
        "thirdNode": "thirdNode",
    }
)

graph.set_entry_point("firstNode")

# Mark both as finish nodes
graph.set_finish_point("secondNode")
graph.set_finish_point("thirdNode")

app = graph.compile()

result = app.invoke({"name": "bob", "age": 30})   # goes to secondNode
print(result['final'])
result = app.invoke({"name": "bobby", "age": 30}) # goes to thirdNode
print(result['final'])

