from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
import random


# ---------------------------
# State Definition
# ---------------------------

class GameState(TypedDict):
    player_name: str
    guesses: List[int]
    attempts: int
    lower_bound: int
    upper_bound: int
    target: int
    last_hint: str
    current_guess: int 

# ---------------------------
# Nodes
# ---------------------------

# Setup node
def setup_node(state: GameState) -> GameState:
    state["target"] = random.randint(1, 200)
    state["attempts"] = 0
    state["guesses"] = []
    state["last_hint"] = ""
    print(f"🎯 Target chosen (hidden)")
    return state


# Guess node (binary search style)
def guess_node(state: GameState) -> GameState:
    guess = (state["lower_bound"] + state["upper_bound"]) // 2
    state["guesses"].append(guess)
    state["attempts"] += 1
    state["current_guess"] = guess
    print(f"🤖 Guess #{state['attempts']}: {guess}")
    return state


# Hint node
def hint_node(state: GameState) -> GameState:
    guess = state["current_guess"]
    target = state["target"]

    if guess == target:
        state["last_hint"] = "correct"
        print("✅ Correct!")
    elif guess < target:
        state["last_hint"] = "higher"
        state["lower_bound"] = guess + 1
        print("🔼 Higher")
    else:
        state["last_hint"] = "lower"
        state["upper_bound"] = guess - 1
        print("🔽 Lower")

    return state


# Router
def continue_router(state: GameState):
    if state["last_hint"] == "correct":
        return "end"
    if state["attempts"] >= 7:
        return "end"
    return "continue"


# ---------------------------
# Graph Construction
# ---------------------------

graph = StateGraph(GameState)

graph.add_node("setup", setup_node)
graph.add_node("guess", guess_node)
graph.add_node("hint", hint_node)

graph.add_edge(START, "setup")
graph.add_edge("setup", "guess")
graph.add_edge("guess", "hint")

graph.add_conditional_edges(
    "hint",
    continue_router,
    {
        "continue": "guess",
        "end": END,
    }
)

app = graph.compile()


# ---------------------------
# Run
# ---------------------------

result = app.invoke({
    "player_name": "Student",
    "guesses": [],
    "attempts": 0,
    "lower_bound": 1,
    "upper_bound": 200,
    "target": 0,
    "last_hint": "",
    "current_guess": 0
})

print("\nFinal State:")
print(result)
