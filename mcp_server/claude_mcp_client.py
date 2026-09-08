import asyncio
import json
import os
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from mcp import Client
from sklearn.metrics.pairwise import cosine_similarity

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv()

user_query = "Is customer C999 active and REFUND 25001 inr?"

TOOL_PERMISSIONS = {
    "get_customer_status": "CUSTOMER_READ",
    "get_customer_balance": "CUSTOMER_READ",
    "refund_customer":"REFUND",
    "delete_customer":"ADMIN",
}

APPROVAL_POLICIES={
    "refund_customer":{
        "approved_required_above":25000,
        "amount_field":"amount"
    }
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
        TOOL_REGISTRY= [{
            "name":t.name,
            "description":t.description,
            "input_schema":t.input_schema,
            "search_text":f"{t.name} : {t.description}"
            }
                         for t in tools_result.tools]

        #KEYWORD SEARCH
        #-----------------------------------
        keyword_results=keyword_tool_search(
            user_query,
            TOOL_REGISTRY
        )

        
        claude_tools = []
        print("\nTools selected by router:")
        selected_tools = route_tools(user_query, TOOL_REGISTRY)


        
        tool_text= [
            tool["search_text"]
            for tool in TOOL_REGISTRY
        ]

        tool_embeddings =embedding_model.encode(tool_text)
       
        query_embedding=embedding_model.encode([user_query])
        similarity = cosine_similarity(
            query_embedding,
            tool_embeddings
        )[0]

        for tool, score in zip(TOOL_REGISTRY,similarity):
            print(f"{tool['name']}:{score:.4f}")
        
        top_indices = similarity.argsort()[-2:][::-1]

        hybrid_results = hybrid_tool_search(
                            TOOL_REGISTRY,
                            similarity,
                            keyword_results
                        )

        for results in hybrid_results:
            print(
                results["tool"]["name"],
                "semantic":result["semantic_score"],
                "keyword":result["keyword_score"],
                "hybrid":result["hybrid_score"]
            )
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
            if not request_approval(tool_name, tool_input):
                print(f"\n--- Approval denied for tool: {tool_name} ---")
                return
            status_response = await execute_mcp_tool(
                mcp_client,
                "get_customer_status",  
                status_input
            )
            if not status_response["success"]:
                print("\n--- Status Check Failed ---")
                print("Error:", status_response["error"])
                return
            status_result = status_response["result"]
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

def requires_approval(tool_name, tool_input):
    # Implement your approval logic here
    # For example, check if the tool requires approval based on the amount
    policy=APPROVAL_POLICIES.get(tool_name)
    if not policy:
        return False
    amount=tool_input.get(policy["amount_field"])

    return amount is not None and amount>policy["approved_required_above"]


def request_approval(tool_name, tool_input):
    # Implement your approval request logic here
    # For example, send an approval request to the appropriate authority
    
    if requires_approval(tool_name, tool_input):
      decision=input(f"Approval required for {tool_name} with amount {tool_input.get('amount', 0)}. Approve? (yes/no): ")
      return decision.lower() == "yes"
    # Simulate approval process
    return True

def route_tools(user_query, tool_registry):
    query = user_query.lower()
    selected_tools = []
    for tool in tool_registry:
        if any(
            keyword in query
            for keyword in tool["description"].lower().split()

               ):
            selected_tools.append(tool)
    return selected_tools


def keyword_tool_search(user_query,tool_registry):
    query= user_query.lower()

    matches=[]

    for tool in tool_registry:
        tool_words = set(tool["search_text"].lower().split())

        query_words=set(query.split())
        overlap= query_words.intersection(tool_words)

        if overlap:
            matches.append({
                "tool":tool,
                "matched_words": overlap
            })
    return matches

def hybrid_tool_search(
        tool_registry,
        semantic_scores,
        keyword_results,
        semantic_weight =0.7,
        keyword_weight=0.3,
        top_k=3
):
    keyword_scores={
        result["tool"]["name"]: result["keyword_score"]
        for result in keyword_results
    }
    ranked_tools = []

    for tool, semantic_scores in zip(
        tool_registry, 
        semantic_scores
    ):
        keyword_score=keyword_scores.get(
            tool["name"],
            0
        )

        hybrid_score=(
            semantic_scores * semantic_weight
            +
            keyword_score * keyword_weight
        )

        ranked_tools.append({
            "tool":tool,
            "semantic_score":semantic_scores,
            "keyword_score": keyword_score,
            "hybrid_score":hybrid_score
        })

        ranked_tools.sort(
            key = lambda x:x["hybrid_score"],
            reverse=True
        )
    return ranked_tools[:top_k]
    

if __name__ == "__main__":
    asyncio.run(main())