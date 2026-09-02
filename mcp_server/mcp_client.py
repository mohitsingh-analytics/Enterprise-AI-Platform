import asyncio
from mcp import Client
async def main():

    async with Client("http://127.0.0.1:8000/mcp") as client:

        print("Connected to:", client.server_info)

        print("\nServer capabilities:")
        print(client.server_capabilities)

        print("\nAvailable tools:")

        tools = await client.list_tools()

        for tool in tools.tools:
            print("\n TOOL: ")
            print("tool","*"*5, tool)
            print("\n Attributed","*"*5)
            print(tool.model_dump())
            print("*"*10)
            print(f"- {tool.name}")
            print(f"  {tool.description}")


        result = await client.call_tool(
            "get_customer_balance",
            {
                "customer_id": "C001"
            }
        )

        print("\nTool result:","***"*10)
        print(result.model_dump_json(indent=2))

        print("\nResult type:","***"*10)
        print(type(result))

        print("\nResult attributes:","***"*10)
        print(dir(result))

        result1 = await client.call_tool(
                    "get_customer_status",
                    {
                        "customer_id": "C001"
                    }
                )
        print("\nTool result:","***"*10)
        print((result1.model_dump_json(indent=2)))

        print("\nResult type:","***"*10)
        print(type(result1))

        print("\nResult attributes:","***"*10)
        print(dir(result1))
        

if __name__=="__main__":
    asyncio.run(main())