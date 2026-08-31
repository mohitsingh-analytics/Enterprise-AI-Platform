from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class AgentState(TypedDict):
    customer_id: str
    amount: int
    approved: bool
    requires_approval: bool
    approval:dict
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
        "approved": decision["approved"],
        "approval":{
            "customer_id":state["customer_id"],
            "amount":state["amount"],
            "tool":"charge_customer"
        }
    }

def revalidation_transaction(state:AgentState):
    print("Revalidation transaction...")
    approval=state["approval"]

    if approval["customer_id"] != state["customer_id"]:
        return{
            "result":"REJECTED: Customer Mismatch"
        }

    if approval["amount"] !=state["amount"]:
        return {
            "result":"REJECTED: Amount mismatch"
        }

    if approval["tool"]!= "charge_customer":
        return {
            "result":"Transaction passed revalidation"
        }

    
def charge_customer(state: AgentState):
    print("Executing charge...")

    return{
        "result": (
            f"Cusomer {state['customer_id']}"
            f"charged INR {state['amount']}"
        )
    }

def policy_check(state:AgentState):
    #for this demo, every payment above INR 10,000
    #requires human approval
    requires_approval =state["amount"] > 10000
    return{
        "requires_approval": requires_approval
    }
def route_after_policy(state:AgentState):
    if state["requires_approval"]:
        return "request_approval"
    return "charge_customer"
    
def route_after_approval(state:AgentState):
    if state["approved"]:
        return "charge_customer"
    return END

def revalidate_transaction(state: AgentState):

    print("Revalidating transaction...")

    # Simulated checks
    transaction_valid = True

    if not transaction_valid:
        return {
            "result": "Transaction failed revalidation."
        }

    return {
        "result": "Transaction passed revalidation."
    }


builder= StateGraph(AgentState)
builder.add_node("policy_check", policy_check)
builder.add_node("request_approval", request_approval)
builder.add_node("charge_customer", charge_customer)

builder.add_edge(START, "policy_check")
builder.add_conditional_edges(
    "policy_check",
    route_after_policy
)

builder.add_conditional_edges(
    "request_approval",
    route_after_approval
)


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
        "requires_approval": False,
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
            "approved": False
        }
    ),
    config=config
)

print("\nFinal result:")
print(result)