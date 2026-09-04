import asyncio
import json
import os

from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from mcp import Client


load_dotenv()

user_query = "Is customer C002 active and what is their current balance?"


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

            status_result = await mcp_client.call_tool(
                "get_customer_status",
                status_input
            )

            print("\nStatus Result:")
            print(status_result.model_dump_json(indent=2))

            # -------------------------------------------------
            # 7. Extract business payload from MCP response
            # -------------------------------------------------

            status_data = json.loads(
                status_result.content[0].text
            )

            status = status_data["status"]

            print("\nCustomer status:", status)

            # -------------------------------------------------
            # 8. APPLICATION POLICY CHECK
            # -------------------------------------------------

            if status.lower() == "active" and balance_input:

                print("\n--- Policy: ACTIVE → Balance allowed ---")

                balance_result = await mcp_client.call_tool(
                    "get_customer_balance",
                    balance_input
                )

                print("\nBalance Result:")
                print(
                    balance_result.model_dump_json(indent=2)
                )

            else:

                print(
                    "\n--- Policy: Customer is NOT ACTIVE "
                    "→ Balance BLOCKED ---"
                )

        else:

            print("\nNo customer status request was provided.")


if __name__ == "__main__":
    asyncio.run(main())