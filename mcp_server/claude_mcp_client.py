import asyncio
import json
import os

from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from mcp import Client


load_dotenv()

user_query = "Is customer C999 active and what is their current balance?"

TOOL_PERMISSIONS = {
    "get_customer_status": "CUSTOMER_READ",
    "get_customer_balance": "CUSTOMER_READ",
    "refund_customer":"REFUND",
    "delete_customer":"ADMIN",
}


async def main():

    # ---------------------------------------------------------
    # 1. Connect to Claude
    # ---------------------------------------------------------
    claude = AsyncAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # ---------------------------------------------------------
    # 2. Connect to MCP Server
    # ---------------------------------------------------------
    async with Client("http://127.0.0.1:8000/mcp") as mcp_client:

        # -----------------------------------------------------
        # 3. Discover tools from MCP Server
        # -----------------------------------------------------
        tools_result = await mcp_client.list_tools()

        claude_tools = []

        for tool in tools_result.tools:

            claude_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
            )

        print("\nTools discovered from MCP:")
        for tool in claude_tools:
            print(tool)

        # -----------------------------------------------------
        # 4. Ask Claude which tools are required
        # -----------------------------------------------------
        response = await claude.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            tools=claude_tools,
            messages=[
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        )

        # -----------------------------------------------------
        # 5. COLLECT Claude's tool requests
        #
        # IMPORTANT:
        # We do NOT execute tools here.
        # We only capture what Claude requested.
        # -----------------------------------------------------
        status_input = None
        balance_input = None

        for block in response.content:

            if block.type == "tool_use":

                tool_name = block.name
                tool_input = block.input

                print("\nClaude requested tool:")
                print("Name:", tool_name)
                print("Input:", tool_input)

                if tool_name == "get_customer_status":

                    status_input = tool_input

                elif tool_name == "get_customer_balance":

                    balance_input = tool_input

        # -----------------------------------------------------
        # 6. APPLICATION ORCHESTRATION
        #
        # Business rule:
        # STATUS must be checked before BALANCE.
        # -----------------------------------------------------

        if status_input:

            print("\n--- Executing STATUS first ---")
            user_permissions = ["CUSTOMER_READ"]  # Example user permissions
            if not authorize_tool(tool_name,user_permissions):
                print(f"\n--- Authorization failed for tool: {tool_name} ---")
                return 
            status_result = await execute_mcp_tool(
                mcp_client,
                "get_customer_status",  
                status_input
            )

            print("\nStatus Result:")
            print(status_result.model_dump_json(indent=2))

            # -------------------------------------------------
            # 7. Extract business payload from MCP response
            # -------------------------------------------------

            status_data = json.loads(status_result.content[0].text)

            # Handle tool-level/business error first
            if "error" in status_data:
                print("\n--- Status Check Failed ---")
                print("Error:", status_data["error"])

                print("\n--- Policy: Customer could not be validated → Balance BLOCKED ---")

            else:
                status = status_data.get("status")

                print("\nCustomer status:", status)

                if status == "ACTIVE" and balance_input:
                    print("\n--- Policy: ACTIVE → Balance allowed ---")

                    balance_result = await execute_mcp_tool(
                        mcp_client,
                        "get_customer_balance",
                        balance_input
                    )

                    print("\nBalance Result:")
                    print(balance_result.model_dump_json(indent=2))

                else:
                    print("\n--- Policy: Customer is NOT ACTIVE → Balance BLOCKED ---")

async def execute_mcp_tool(mcp_client, tool_name, tool_input):
    try:
        result=await mcp_client.call_tool(tool_name,tool_input)
        return{
            "success":True,
            "result":result,
            "error":None
              }
    except Exception as e:
        print(f"\n MCP Tool execution failed: {tool_name}")
        print("Technical error:",str(e))
        return{
            "success":False,
            "result":None,
            "error":"The service requested is currently unavailable. Please try again later."
        }

def authorize_tool(tool_name,user_permissions):
    # Implement your authorization logic here
    # For example, check if the user has the required permissions for the tool
    if tool_name=="get_customer_status" and "CUSTOMER_READ" not in user_permissions:
        return False
    return True


if __name__ == "__main__":
    asyncio.run(main())