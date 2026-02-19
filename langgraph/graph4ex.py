from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from PIL import Image as PILImage
from io import BytesIO


# --- Define your agent state ---
class AgentState(TypedDict):
    number1: int
    number2: int
    operation1: str
    operation2: str
    result: int


# --- First operation ---
def adder1(state: AgentState) -> AgentState:
    state["result"] = state["number1"] + state["number2"]
    return state


def subtractor1(state: AgentState) -> AgentState:
    state["result"] = state["number1"] - state["number2"]
    return state


def router1(state: AgentState):
    if state["operation1"] == "+":
        return "addition1"
    elif state["operation1"] == "-":
        return "subtraction1"


# --- Second operation ---
def adder2(state: AgentState) -> AgentState:
    state["result"] = state["result"] + state["number2"]
    return state


def subtractor2(state: AgentState) -> AgentState:
    state["result"] = state["result"] - state["number2"]
    return state


def router2(state: AgentState):
    if state["operation2"] == "+":
        return "add2"
    elif state["operation2"] == "-":
        return "subtraction2"


# --- Create graph ---
graph = StateGraph(AgentState)

# Nodes
graph.add_node("router1", lambda state: state)
graph.add_node("addition1", adder1)
graph.add_node("subtraction1", subtractor1)

graph.add_node("router2", lambda state: state)
graph.add_node("addition2", adder2)
graph.add_node("subtraction2", subtractor2)

# Flow
graph.add_edge(START, "router1")

graph.add_conditional_edges(
    "router1",
    router1,
    {
        "addition1": "addition1",
        "subtraction1": "subtraction1",
    }
)

graph.add_edge("addition1", "router2")
graph.add_edge("subtraction1", "router2")

graph.add_conditional_edges(
    "router2",
    router2,
    {
        "add2": "addition2",
        "subtraction2": "subtraction2",
    }
)

graph.add_edge("addition2", END)
graph.add_edge("subtraction2", END)

app = graph.compile()

result = app.invoke({
    "number1": 5,
    "number2": 3,
    "operation1": "+",
    "operation2": "+"
})

print(result["result"])


# --- Get PNG bytes ---
png_bytes = app.get_graph().draw_mermaid_png()

# --- Convert to image and show ---
img = PILImage.open(BytesIO(png_bytes))
img.show()  # This will open the image in your default image viewer

# --- Optional: Save to file ---
img.save("graph.png")