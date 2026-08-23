from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool

@tool
def get_customer_balance(customer_id:str):
    return f"Customer{customer_id} balance is $2500"

@tool
def get_customer_status(customer_id: str):
    """Get the current balance for a customer"""
    return f"Customer {customer_id} balance is $25000"



class AgentState(TypedDict):
    question: str
    tool_name: str
    customer_id: str
    tool_result: str
    answer: str


def execute_tool(state:AgentState):
    if state["tool_name"] == "get_customer_balance":
        result= get_customer_balance.invoke({
            "customer_id": state["customer_id"]
            })

    elif state["tool_name"] == "get_customer_status":
        result= get_customer_status.invoke({
            "customer_id": state["customer_id"]
            })

    else:
        result = "unknown tool"

    return{
        "tool_result":result
    }

def tool_router(state: AgentState):

    question = state["question"].lower()

    if "balance" in question:
        return "get_customer_balance"

    if "status" in question:
        return "get_customer_status"

    return "none"


def route_tool(state: AgentState):

    tool_name = tool_router(state)

    if tool_name == "none":
        return "answer"

    return "tool"

def answer_node(state: AgentState):

    print("Generating answer...")

    return {
        "answer": f"Answer based on: {state['tool_name']} with answer as {state['answer']}"
    }
from langgraph.graph import StateGraph, START, END

def tool_selection_node(state: AgentState):

    return {
        "tool_name": tool_router(state)
    }


builder = StateGraph(AgentState)

builder.add_node("tool_selection", tool_selection_node)
builder.add_node("execute_tool", execute_tool)
builder.add_node("answer", answer_node)

builder.add_edge(START, "tool_selection")

builder.add_conditional_edges(
    "tool_selection",
    route_tool,
    {
        "tool": "execute_tool",
        "answer": "answer"
    }
)

builder.add_edge("execute_tool", "answer")
builder.add_edge("answer", END)

graph = builder.compile()




result = graph.invoke(
    {
        "question": "What is the balance for customer C001?",
        "tool_name": "",
        "customer_id": "C001",
        "tool_result": "",
        "answer": ""
    }
)

print(result)