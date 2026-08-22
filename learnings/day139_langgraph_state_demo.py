from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    question: str
    request_type: str
    research: str
    calculation: str
    answer: str

def research_node(state: AgentState):
    print("Researching ....")
    return {
        "research": f"Research completed for: {state['question']}"}

def answer_node(state: AgentState):
    print("Answering ....")
    return {
        "answer": f"Answer completed for: {state['research']}"}

def calculation_node(state: AgentState):

    print("Running calculation...")

    return {
        "calculation": "Calculation completed."
    }

def classify_node(state: AgentState):
    question = state["question"].lower()
    if "calculate" in question or "how much" in question:
        request_type = "calculation"
    elif "approve" in question or "approval" in question:
        request_type = "human"
    else:
        request_type = "research"
    return {
        "request_type" : request_type
    }

def human_review_node(state: AgentState):

    print("Human review required.")

    return {
        "answer": "Request requires human approval."
    }

def route_request(state: AgentState):

    if state["request_type"] == "research":
        return "research"

    if state["request_type"] == "calculation":
        return "calculation"

    return "human_review"

builder = StateGraph(AgentState)


builder.add_node("classify", classify_node)
builder.add_node("research", research_node)
builder.add_node("calculation", calculation_node)
builder.add_node("human_review", human_review_node)
builder.add_node("answer", answer_node)


builder.add_edge(START, "classify")


builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "research": "research",
        "calculation": "calculation",
        "human_review": "human_review"
    }
)
builder.add_edge("calculation", "answer")
builder.add_edge("research", "answer")
builder.add_edge("human_review", END)
builder.add_edge("answer", END)
graph= builder.compile()


result = graph.invoke(
    {
        "question": "How much is the reimbursement?",
        "request_type": "",
        "research": "",
        "calculation": "",
        "answer": ""
    }
)

print(result)