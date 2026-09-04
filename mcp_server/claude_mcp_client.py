import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from anthropic import AsyncAnthropic
from mcp import Client
user_query = " is customer C001 active and what is their current balance?"
async def main():
    claude=AsyncAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    async with Client("http://127.0.0.1:8000/mcp") as mcp_client:
        #Discover tools from MCP
        tools_result= await mcp_client.list_tools()
        claude_tools=[]
        for tool in tools_result.tools:
            claude_tools.append(
                {
                    "name":tool.name,
                    "description":tool.description,
                    "input_schema":tool.input_schema,
                }
            )

        response = await claude.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            tools=claude_tools,
            messages=[
                {
                    "role":"user",
                    "content":user_query
                }
            ]
        )

        #we will connect claude here next.
        for block in response.content:
            if block.type=="tool_use":
                tool_name=block.name
                tool_input=block.input
                
                print("\n Claude requested tool:")
                print("Name:", tool_name)
                print("Input:", tool_input)
                
                if tool_name == "get_customer_status":

                    tool_result = await mcp_client.call_tool(
                        tool_name,
                        tool_input
                    )

                    print("\n Tool Result")
                    print(tool_result.model_dump_json(indent=2))

                elif tool_name == "get_customer_balance":

                    print("\n Application Policy Check:")
                    print("Balance lookup requires customer to be ACTIVE.")

                    # Don't execute yet
                    print("Balance tool execution is currently BLOCKED.")
                
        #         final_response= await claude.messages.create(
        #             model="claude-sonnet-4-5",
        #             max_tokens=500,
        #             tools=claude_tools,
        #             messages=[
        #                 {
        #                     "role":"user",
        #                     "content":user_query
        #                 },
        #                 {
        #                     "role":"assistant",
        #                     "content":response.content
        #                 },
        #                 {
        #                     "role":"user",
        #                     "content":[
        #                             {
        #                             "type":"tool_result",
        #                             "tool_use_id":block.id,
        #                             "content":str(tool_result)
        #                          }
        #                         ]
        #                      }
        #                 ]
        #         )
        # for block in final_response.content:
        #     if block.type == "text":
        #         print("\nFinal answer:")
        #         print(block.text)
if __name__=="__main__":
    asyncio.run(main())