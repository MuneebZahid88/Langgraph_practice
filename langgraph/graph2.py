from typing import TypedDict
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    value: list[int]
    operation: str
    result: str


def operator_agent(state: AgentState) -> AgentState:
    """operator_agent to perform some operation"""

    if state["operation"] == "+":
        total = sum(state["value"])
        state["result"] = f"Hey {state['name']} result is {total}"

    else:
        product = 1
        for num in state["value"]:
            product *= num
        state["result"] = f"Hey {state['name']} result is {product}"

    return state


graph = StateGraph(AgentState)

graph.add_node("operator_agent", operator_agent)

graph.set_entry_point("operator_agent")
graph.set_finish_point("operator_agent")

app = graph.compile()

result = app.invoke({
    "name": "bob",
    "value": [2, 3, 4],
    "operation": "+",
    "result": ""
})

print(result["result"])
