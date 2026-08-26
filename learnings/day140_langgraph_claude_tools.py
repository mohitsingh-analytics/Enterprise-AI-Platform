from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from typing import Annotated
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
checkpointer= InMemorySaver()
load_dotenv()

@tool
def get_customer_balance(customer_id:str):
    """get the current account balance for a customer"""
    return f"customer {customer_id} balance is INR 25000"

@tool
def get_customer_status(customer_id: str):
    """get the customer account status"""
    return f"customer {customer_id} is ACTIVE"

@tool
def charge_customer(customer_id:str, amount:float):
    """charge a customer a specific amount"""
    return f"customer {customer_id} charged INR {amount}"

def validate_tool_call(tool_call, user_context):
    tool_name=tool_call["name"]
    policy=tool_policies.get(tool_name)
    if not policy:
        raise ValueError("Unknown Tool")

    if not authorize_tool

tools=[
    get_customer_balance,
    get_customer_status,
    charge_customer,
]

llm= ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
)

tool_policies = {

    "get_customer_balance": {
        "risk": "LOW",
        "requires_approval": False
    },

    "get_customer_status": {
        "risk": "LOW",
        "requires_approval": False
    },

    "update_customer": {
        "risk": "HIGH",
        "requires_approval": True
    },

    "charge_customer": {
        "risk": "CRITICAL",
        "requires_approval": True
    }
}


user_context = {
    "user_id": "USER-001",
    "role": "analyst"
}

def tool_authorization(tool_name,user_context):
    policy= tool_policies.get(tool_name)
    if not policy:
        return False
    if tool_name=="charge_customer":
        return user_context["role"]=="finance admin"
    return True

def authorize_tool(tool_name, user_context):

    role = user_context["role"]

    if tool_name == "charge_customer":
        return role == "finance_admin"

    if tool_name == "delete_customer":
        return role == "customer_admin"

    return True

def validate_tool_call(tool_call, user_context):

    tool_name = tool_call["name"]

    policy = tool_policies.get(tool_name)

    if not policy:
        raise ValueError("Unknown tool")

    if not authorize_tool(tool_name, user_context):
        raise PermissionError(
            f"User not authorized for {tool_name}"
        )

    if policy["requires_approval"]:
        raise PermissionError(
            f"Human approval required for {tool_name}"
        )

    return True

llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    approval_required: bool

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


def approval_node(state):

    print("\n*** HUMAN APPROVAL REQUIRED ***")

    return {
        "approval_required": True
    }

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

graph = builder.compile(
    checkpointer=checkpointer
)


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