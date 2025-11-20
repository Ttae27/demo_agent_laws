from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from rag.query import query_rag
from model import get_llm

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str

tools = [query_rag]
llm = get_llm()
llm_with_tools = llm.bind_tools(tools)

def query_agent(state: AgentState) -> AgentState:
    query = HumanMessage(content=state['query'])
    state["messages"] = [query]
    return state

def agent(state: AgentState) -> AgentState:
    system_msg = SystemMessage(content=(
    """
    You are an AI assistant specialized in answering questions using two tools:
    1. RAG Tool – retrieves information from documents related to law, finance and procurement.
    2. Math Tool – performs precise mathematical calculations.

    The user will often communicate in Thai. You MUST understand Thai perfectly.

    [behavior rules]:
    - First, interpret the user's intent (in Thai or English).
    - If the question requires factual information, definitions, or explanations from stored documents → use the RAG tool.
    - When using RAG tool, you don't need to change query from users except it's has a typo.
    - If the question requires numerical calculation, comparison, or formula-based reasoning → use the Math tool.
    - If the user mixes both (e.g., “ตามเอกสารหน้าที่ 2 ราคาสินค้าเท่าไหร่ และรวมภาษี 7% เท่าไหร่”) → 
        1) use the RAG tool to retrieve relevant context  
        2) then send the number(s) to the Math tool to compute the result.
    - Never guess information not found in retrieval.
    - Always reason step-by-step and choose the correct tool before responding.
    - Final answer must be in Thai unless the user asks otherwise.
"""))
    
    messages = [system_msg] + state['messages']
    ai_message = llm_with_tools.invoke(messages)
    state['messages'].append(ai_message)

    return state

def should_continue(state: AgentState):
    message = state["messages"][-1]
    
    if not message.tool_calls:
        print("Content: ", state["messages"][-2].content)
        return "end"
    else:
        print("Content: ", state["messages"][-2].content)
        print("Tools: ", message.tool_calls)
        print("-"*100)
        return "continue"

def call_tool(state: AgentState):
    tools_by_name = {tool.name: tool for tool in tools}
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"]) 

        state["messages"].append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"]
        ))

    return state

def run_graph(query: str):
    graph = StateGraph(AgentState)

    graph.add_node("query", query_agent)
    graph.add_node("agent", agent)
    graph.add_node("tools", call_tool)

    graph.add_edge(START, "query")
    graph.add_edge("query", "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    graph.add_edge("tools", "agent")
    app = graph.compile()
    result = app.invoke({"query": query})

    return result['messages'][-1].content

def pure_llm(query):
    query = [HumanMessage(content=query)]
    result = llm.invoke(query)
    return result.content
