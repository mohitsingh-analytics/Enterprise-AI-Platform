from mcp.server.mcpserver import MCPServer

server = MCPServer("CustomerService")

print("MCP Server created:", server)

@mcp.tool()
def get_customer_balance(customer_id: str):
    """Get the current balance for a customer """
    balances = {
        "C001": 25000,
        "C002": 10000,
    }
    balance = balances.get(customer_id)

    if balance is None:
        return{
            "customer_id":customer_id,
            "error":"Customer not found"
        }
    return{
        "customer_id":customer_id,
        "amount": balance,
        "currency":"INR"
    }

