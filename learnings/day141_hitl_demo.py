from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class AgentState(TypedDict):
    customer_id: str
    amount: int
    approved: bool
    result: str

def request_approval(state: AgentState):
    print("Entering Approval Node..")

    decision = interrupt({
    "type": "payment_approval",
    "customer_id": state["customer_id"],
    "amount": state["amount"],
    "message": "Approval required before charging customer."
    })

    print("RESUMED DECISION:", decision)

    return {
        "approved": decision["approved"]
    }

def charge_customer(state: AgentState):
    print("Executing charge...")

    return{
        "result": (
            f"Cusomer {state['customer_id']}"
            f"charged INR {state['amount']}"
        )
    }

builder= StateGraph(AgentState)
builder.add_node("request_approval", request_approval)
builder.add_node("charge_customer", charge_customer)

builder.add_edge(START, "request_approval")
builder.add_edge("request_approval","charge_customer")
builder.add_edge("charge_customer",END)

checkpointer=InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)

config={
    "configurable":{
        "thread_id":"payment-001"
    }
}

result=graph.invoke(
    {
        "customer_id":"C001",
        "amount":50000,
        "approved":False,
        "result":""
    },
    config=config
)

print("\n workflow result:")
print(result)

print("\n--- Human approved ---")

result = graph.invoke(
    Command(
        resume={
            "approved": True
        }
    ),
    config=config
)

print("\nFinal result:")
print(result)