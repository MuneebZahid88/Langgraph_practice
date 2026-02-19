from typing import TypedDict
from langgraph.graph import StateGraph, END,START
from PIL import Image as PILImage
from io import BytesIO
import random


class AgentState(TypedDict):
    name: str
    number: list[int]
    counter: int


def greeting_node(state: AgentState) -> AgentState:
    state["name"] = "hi there " + state["name"]
    state["counter"] = 0
    return state


def random_node(state: AgentState) -> AgentState:
    state["number"].append(random.randint(1, 10))
    state["counter"] += 1
    return state


def continue_node(state: AgentState):
    if state["counter"] < 5:
        return "loop"
    else:
        return "end"


graph = StateGraph(AgentState)

graph.add_node("greeting", greeting_node)
graph.add_node("random", random_node)

graph.add_edge(START, "greeting")
graph.add_edge("greeting", "random")

graph.add_conditional_edges(
    "random",
    continue_node,
    {
        "loop": "random",
        "end": END,
    }
)

app = graph.compile()

result = app.invoke({
    "name": "Alice",
    "number": [],
    "counter": 0
})

print(result)




# --- Get PNG bytes ---
png_bytes = app.get_graph().draw_mermaid_png()

# --- Convert to image and show ---
img = PILImage.open(BytesIO(png_bytes))
img.show()  # This will open the image in your default image viewer

# --- Optional: Save to file ---
img.save("graph.png")