from typing import TypedDict, Union
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class AgentState(TypedDict):
    messages: list[Union[HumanMessage, AIMessage]]

# ✅ Use OpenRouter instead of OpenAI
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemini-2.5-flash-lite-preview-09-2025",  
)

def process(state: AgentState) -> AgentState:
    """This node will solve request and return response"""
    # Only send last 5 messages to LLM
    last_messages = state["messages"][-5:]
    response = llm.invoke(last_messages)
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nResponse: {response.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()

# ----------------------------
# Load previous conversation if exists
conversation_history = []
if os.path.exists("logging.txt"):
    with open("logging.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("You: "):
                conversation_history.append(HumanMessage(content=line[len("You: "):].strip()))
            elif line.startswith("AI: "):
                conversation_history.append(AIMessage(content=line[len("AI: "):].strip()))

# Start conversation
user_input = input("Enter: ")
while user_input.lower() != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    
    # Send only last 5 messages to the LLM
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result["messages"]
    
    user_input = input("Enter: ")

# Save conversation
# Save conversation
with open("logging.txt", "w", encoding="utf-8") as file:
    file.write("Your Conversation Log:\n")
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")
