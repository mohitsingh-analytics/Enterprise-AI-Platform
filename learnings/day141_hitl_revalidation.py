from langgraph.types import interrupt, Command
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
class AgentState(TypedDict):
    customer_id:str
    amount: int
    requires_approval:bool
    approved:bool
    approval:dict
    validation_passed:bool
    result:str

def revalidate_transaction(state:AgentState):
    print("Revalidating transaction...")
    approval=state["approval"]

    #check 1: Customer must matched approved request
    if approval["customer_id"] != state["customer_id"]:
        print("REJECTED: Customer Mismatch")
        return {"validation_passed": False }

    #check 2: Amount must match approved request
    if approval["amount"] !=state["amount"]:
        print("REJECTED: Amount mismatch")
        return{"validation_passed": False}

    #check 3: Tool must match approved operation
    if approval["tool"] != "charge_customer":
        print("Rejected: Tool mismatch")
        return {"validation_passed": False}

    print("Revalidation Successful")
    return {"validation_passed": True}


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
def route_after_policy(state: AgentState):
    if state["requires_approval"]:
        return "request_approval"

    return "charge_customer"

def route_after_approval(state: AgentState):
    if state["approved"]:
        return "revalidate_transaction"

    return END

builder= StateGraph(AgentState)
builder.add_node("policy_check", policy_check)
builder.add_node("request_approval", request_approval)
builder.add_node("revalidate_transaction",revalidate_transaction)
builder.add_node("charge_customer", charge_customer)

## policy Check -> revalidate transaction -> if yes, request approval -> charge customer

## policy Check -> revalidate transaction -> if no, then transaction failed
def route_after_revalidation(state: AgentState):

    if state["validation_passed"]:
        return "charge_customer"

    return END

builder.add_edge(START, "policy_check")

builder.add_conditional_edges(
    "policy_check",
    route_after_policy
)

builder.add_conditional_edges(
    "request_approval",
    route_after_approval
)

builder.add_conditional_edges(
    "revalidate_transaction",
    route_after_revalidation
)

builder.add_edge("charge_customer", END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

config= {
    "configurable":{
        "thread_id": "payment-001"
    }
}

result = graph.invoke(
    {
        "customer_id": "c001",
        "amount": 50000,
        "approved": False,
        "requires_approval":False,
        "result":""

    },
    config = config
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