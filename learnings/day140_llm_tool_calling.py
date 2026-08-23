import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

load_dotenv()

@tool
def get_customer_balance(customer_id:str):
    """get the current account balance for a customer"""
    return f"Customer {customer_id} balance is INR 25000"

@tool
def get_customer_status(customer_id:str):
    """get the customer accounnt status for a customer"""
    return f"Customer {customer_id} status is ACTIVE"

tools=[
    get_customer_balance,
    get_customer_status
]

llm=ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
)

llm_with_tools= llm.bind_tools(tools)

questions="what is the balance for the customer C001"

response=llm_with_tools.invoke(questions)

print("\nclaude response:")
print(response)

print("\n Tool calls:")
print(response.tool_calls)


tool_call = response.tool_calls[0]
selected_tool={
    tool.name:tool
    for tool in tools
}[tool_call["name"]]

tool_result=selected_tool.invoke(
    tool_call["args"]
)

print("\n Tool Result:")
print(tool_result)

