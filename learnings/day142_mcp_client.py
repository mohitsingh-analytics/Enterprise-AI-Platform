import asyncio
from mcp import Client
from mcp.server import MCPServer

mcp=MCPServer("CustomerService")

@mcp.tool()
def get_customer_balance(customer_id:str):
    """Get the account balance for a customer"""
    balances={
        "C001": 25000,
        "C002":10000,
    }
    balance=balances.get(customer_id)
    if balance is None:
        return{
            "customer_id": customer_id,
            "error":"Customer not found"
        }
    return{
        "customer_id":customer_id,
        "amount":balance,
        "currency":"INR"
    }

async def main():
    async with Client(mcp) as client:
        print("Connected to:", client.server_info)
        print("capabilities", client.server_capabilities)
        tools=await client.list_tools()
        print("\n Available Tools:")

        for tool in tools.tools:
            print(
                tool.name,"->",tool.description
            )
        result =await client.call_tool(
            "get_customer_balance",
            {
                "customer_id":"C001"
            }   
        )
        print("\n Result of get_customer_balance:",result)
asyncio.run(main())

