from mcp.server.mcpserver import MCPServer
import inspect
mcp=MCPServer("CustomerService")

@mcp.tool()
def get_customer_status(customer_id:str):
    """Get the status of a customer"""
    statuses={
        "C001":"Active",
        "C002":"Suspended",
    }
    status=statuses.get(customer_id)
    if status is None:
        return{
            "customer_id": customer_id,
            "error":"Customer not found"
        }
    return{
        "customer_id":customer_id,
        "status":status
    }


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

print(dir(MCPServer))
print("*****"*5,inspect.signature(MCPServer.run_streamable_http_async))

import asyncio  
if __name__=="__main__":
    asyncio.run(
        mcp.run_streamable_http_async(
            host="127.0.0.1",
            port=8000,
            streamable_http_path="/mcp"
        )
    )

    