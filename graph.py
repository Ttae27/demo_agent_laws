from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from rag.query import query_rag
from rag.query import check_budget_discipline_s20
from model import get_llm

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    mode: str  

all_tools = [query_rag, check_budget_discipline_s20]
llm = get_llm()

def query_agent(state: AgentState) -> AgentState:
    query = HumanMessage(content="[current]: " + state['query'])
    state["messages"] = [query]
    return state

def agent(state: AgentState) -> AgentState:
    mode = state["mode"]
    print(mode)
    
    if mode == 'document':
        llm_with_tools = llm.bind_tools(all_tools)
        
        system_content = """
        You are an AI assistant specialized in answering questions based on [current] message.
        You have access to two tools: 'query_rag' and 'check_budget_discipline_s20'.
        
        [behavior rules]:
        - Analyze user intent to choose the correct tool:
            - Use 'query_rag' for questions about text, definitions, or legal clauses.
            - Use 'check_budget_discipline_s20' for questions involving specific budget numbers calculation.
        - Answer based ONLY on the output provided by the used tool.
        - If both 'query_rag' and 'check_budget_discipline_s20' are used and no answer is found, respond with “ไม่พบข้อมูลในเอกสาร”.
        - Answer in Thai.
        """
    else:
        llm_with_tools = llm  
        
        system_content = """
        You are a helpful AI assistant. 
        You can answer general questions, chat, and help with various tasks based on your general knowledge.
        You DO NOT have access to any specific user documents.
        Answer in Thai.
        """

    system_msg = SystemMessage(content=system_content)
    
    messages = [system_msg] + state['messages']
    
    ai_message = llm_with_tools.invoke(messages)
    state['messages'].append(ai_message)

    return state

def should_continue(state: AgentState):
    message = state["messages"][-1]
    
    if not message.tool_calls:
        return "end"
    else:
        print(f"Tools triggered: {message.tool_calls}")
        return "continue"

def call_tool(state: AgentState):
    tools_by_name = {tool.name: tool for tool in all_tools}
    
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        
        try:
            result = tool.invoke(tool_call["args"])
        except Exception as e:
            result = f"Error executing tool: {str(e)}"

        state["messages"].append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"]
        ))

    return state

def run_graph(query: str, mode: str = "general", history: list = []):
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

    chat_history = []
    for msg in history:
        if msg.get("sender") == "user":
            chat_history.append(HumanMessage(content=msg.get("text", "")))
        elif msg.get("sender") == "bot":
            chat_history.append(AIMessage(content=msg.get("text", "")))
    
    result = app.invoke({
        "query": query, 
        "mode": mode,
        "messages": chat_history 
    })

    last_message = result['messages'][-1]
    content = last_message.content

    if isinstance(content, list):
        text_content = "".join([
            block.get("text", "") for block in content 
            if isinstance(block, dict) and block.get("type") == "text"
        ])
        return text_content
    
    return str(content)