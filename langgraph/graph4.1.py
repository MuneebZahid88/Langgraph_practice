from typing import TypedDict
from langgraph.graph import StateGraph, END,START
from PIL import Image as PILImage
from io import BytesIO

# --- Define your agent state ---
class AgentState(TypedDict):
    number1: int
    number2: int
    operation: str
    result: int

# --- Define your nodes ---
def adder(state: AgentState) -> AgentState:
    state["result"] = state["number1"] + state["number2"]
    return state


def subtractor(state: AgentState) -> AgentState:
    state["result"] = state["number1"] - state["number2"]
    return state

def router(state: AgentState) -> AgentState:
    if state["operation"] == "+":
        return "addition"
    elif state["operation"] == "-":
        return "subtraction"



graph = StateGraph(AgentState)

graph.add_node("router", lambda state: state)  # Dummy node for routing
graph.add_node("addition", adder)
graph.add_node("subtraction", subtractor)


graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    router,
    {
        "addition": "addition",
        "subtraction": "subtraction",
    }
)
graph.add_edge("addition", END)
graph.add_edge("subtraction", END)

app = graph.compile()

result = app.invoke({"number1": 5, "number2": 3, "operation": "-"})  
print(result["result"])

# --- Get PNG bytes ---
png_bytes = app.get_graph().draw_mermaid_png()

# --- Convert to image and show ---
img = PILImage.open(BytesIO(png_bytes))
img.show()  # This will open the image in your default image viewer

# --- Optional: Save to file ---
img.save("graph.png")