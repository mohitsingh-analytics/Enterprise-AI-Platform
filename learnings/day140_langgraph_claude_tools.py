from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from typing import Annotated
from typing import TypedDict

load_dotenv()

@tool
def get_customer_balance(customer_id:str):
    """get the current account balance for a customer"""
    return f"customer {customer_id} balance is INR 25000"

@tool
def get_customer_status(customer_id: str):
    """get the customer account status"""
    return f"customer {customer_id} is ACTIVE"

tools=[
    get_customer_balance,
    get_customer_status
]

llm= ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def agent_node(state: AgentState):
    print("*****INSIDE agent_node*****")
    response=llm_with_tools.invoke(
        state["messages"]
    )
    return{
        "messages": [response]
    }

tool_node = ToolNode(tools)



def route_after_agent(state:AgentState):
    print("*****INSIDE route_after_agent*****")
    last_message=state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        END: END,
    }
)

builder.add_edge("tools", "agent")

graph = builder.compile()


result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is the balance for customer C001?"
            }
        ]
    }
)

for i, message in enumerate(result["messages"], start=1):
    print(f"\nMESSAGE {i}")
    print("Type:", type(message).__name__)
    print("Content:", message.content)

    if hasattr(message, "tool_calls"):
        print("Tool calls:", message.tool_calls)

print("\nConversation:")
for message in result["messages"]:
    print("\n---")
    print(message)