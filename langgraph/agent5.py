import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
from operator import add as add_messages

# Pinecone & LangChain Imports
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

load_dotenv()

# --- 1. CONFIGURATION ---
# Using the index name for your project
INDEX_NAME = "project-py" 

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemini-2.5-flash-lite-preview-09-2025",
    temperature=0,  
)

# Try this first: setting the dimensions to match your index
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1024 
)

# --- 2. CONNECT TO EXISTING PINECONE INDEX ---
# We bypass the chunking and uploading entirely
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    namespace="example-namespace"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# --- 3. TOOLS & GRAPH LOGIC ---
@tool
def retriever_tool(query: str) -> str:
    """Searches the 'project-py' knowledge base for relevant data."""
    docs = retriever.invoke(query)
    
    if not docs:
        return "No relevant information found in the project-py database."
    
    results = []
    for i, d in enumerate(docs):
        # This checks the common metadata keys used by different loaders
        # 'text' is standard for some, 'page_content' for others
        content = d.page_content or d.metadata.get("text") or d.metadata.get("content")
        
        if content:
            results.append(f"Source Material {i+1}:\n{content}")
        else:
            # If we still can't find it, let's see what the keys actually are
            keys = list(d.metadata.keys())
            results.append(f"Source {i+1}: [Content missing. Available metadata keys: {keys}]")
    
    return "\n\n".join(results)

    
tools = [retriever_tool]
llm_with_tools = llm.bind_tools(tools)
tools_dict = {t.name: t for t in tools}

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def call_llm(state: AgentState):
    system_prompt = (
        "You are an expert analyst. Answer user questions using the 'project-py' "
        "retriever tool. Always cite the information retrieved."
    )
    messages = [SystemMessage(content=system_prompt)] + state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages': [response]}

def take_action(state: AgentState):
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"Searching project-py for: {t['args'].get('query')}...")
        content = tools_dict[t['name']].invoke(t['args'])
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(content)))
    return {'messages': results}

def should_continue(state: AgentState):
    last_msg = state['messages'][-1]
    return "retriever_agent" if (hasattr(last_msg, 'tool_calls') and last_msg.tool_calls) else END

# --- 4. GRAPH ASSEMBLY ---
workflow = StateGraph(AgentState)
workflow.add_node("llm", call_llm)
workflow.add_node("retriever_agent", take_action)

workflow.set_entry_point("llm")
workflow.add_conditional_edges("llm", should_continue)
workflow.add_edge("retriever_agent", "llm")

rag_agent = workflow.compile()

# --- 5. RUNNER ---
if __name__ == "__main__":
    print(f"=== AGENT CONNECTED TO PINECONE: {INDEX_NAME} ===")
    while True:
        user_input = input("\nQuery: ")
        if user_input.lower() in ['exit', 'quit']: break
        
        result = rag_agent.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"\n[AI]: {result['messages'][-1].content}")