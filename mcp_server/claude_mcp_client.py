import asyncio
import json
import os

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from mcp import Client
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# 1. INITIALIZATION
# =========================================================

load_dotenv()

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

user_query = "Is customer C999 active and REFUND 25001 inr?"

user_permissions = [
    "CUSTOMER_READ",
    "REFUND",
]


# =========================================================
# 2. TOOL PERMISSIONS
# =========================================================

TOOL_PERMISSIONS = {
    "get_customer_status": "CUSTOMER_READ",
    "get_customer_balance": "CUSTOMER_READ",
    "refund_customer": "REFUND",
    "delete_customer": "ADMIN",
}


# =========================================================
# 3. APPROVAL POLICIES
# =========================================================

APPROVAL_POLICIES = {
    "refund_customer": {
        "approved_required_above": 25000,
        "amount_field": "amount",
    }
}


# =========================================================
# 4. STOP WORDS
# =========================================================

STOP_WORDS = {
    "is",
    "are",
    "the",
    "a",
    "an",
    "and",
    "or",
    "in",
    "of",
    "to",
    "for",
}


# =========================================================
# 5. TOOL METADATA
# =========================================================

TOOL_METADATA = {
    "get_customer_status": {
        "domain": "customer",
        "capabilities": [
            "check customer status",
            "determine whether customer is active",
            "verify customer account status",
        ],
    },

    "get_customer_balance": {
        "domain": "customer",
        "capabilities": [
            "check customer balance",
            "retrieve account balance",
            "find money available in customer account",
        ],
    },

    "refund_customer": {
        "domain": "customer",
        "capabilities": [
            "refund customer",
            "return money to customer",
            "process customer refund",
        ],
    },
}


# =========================================================
# 6. MAIN APPLICATION
# =========================================================

async def main():

    # -----------------------------------------------------
    # 1. Connect to Claude
    # -----------------------------------------------------

    claude = AsyncAnthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # -----------------------------------------------------
    # 2. Connect to MCP Server
    # -----------------------------------------------------

    async with Client(
        "http://127.0.0.1:8000/mcp"
    ) as mcp_client:

        # -------------------------------------------------
        # 3. Discover tools from MCP Server
        # -------------------------------------------------

        tools_result = await mcp_client.list_tools()

        TOOL_REGISTRY = []

        for tool in tools_result.tools:

            tool_name = tool.name

            # Safely read metadata.
            # If metadata is not available, use an empty list.
            capabilities = TOOL_METADATA.get(
                tool_name,
                {}
            ).get(
                "capabilities",
                []
            )

            search_text = (
                f"{tool.name} "
                f"{tool.description} "
                f"{' '.join(capabilities)}"
            )

            TOOL_REGISTRY.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                    "search_text": search_text,
                }
            )

        # -------------------------------------------------
        # Inspect MCP tool registry
        # -------------------------------------------------

        print("\nRegistry type:", type(TOOL_REGISTRY))

        for tool in TOOL_REGISTRY:
            print("Tool:", tool.get("name"))
            print("Description:", tool.get("description"))
            print("Search text:", tool.get("search_text"))
            print("---")

        # =================================================
        # 4. INTENT DECOMPOSITION
        # =================================================

        llm_decom_query = (
            "What independent tasks does the user want to "
            "accomplish using this query?\n\n"
            f"Query: {user_query}"
        )

        decomposition_response = await claude.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,

            system="""
You are a task decomposition engine.

Decompose the user's request into independent tasks.

For every task:
- Preserve all explicitly stated information relevant to that task.
- Do not invent, assume, or infer missing information.
- Do not add tool-specific fields or schemas.
- Keep each task self-contained.

If information in the user's request clearly applies to a task,
preserve that information in that task's description, even if it
was stated in another part of the request.

Do not omit explicitly stated entities, identifiers, amounts,
currencies, dates, or other relevant information.
""",

            messages=[
                {
                    "role": "user",
                    "content": llm_decom_query,
                }
            ],

            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",

                        "properties": {
                            "tasks": {
                                "type": "array",

                                "items": {
                                    "type": "object",

                                    "properties": {
                                        "task_name": {
                                            "type": "string",
                                        },

                                        "description": {
                                            "type": "string",
                                        },
                                    },

                                    "required": [
                                        "task_name",
                                        "description",
                                    ],

                                    "additionalProperties": False,
                                },
                            },
                        },

                        "required": [
                            "tasks",
                        ],

                        "additionalProperties": False,
                    },
                }
            },
        )

        # -------------------------------------------------
        # Parse decomposition response
        # -------------------------------------------------

        task_plan = None

        for block in decomposition_response.content:

            if block.type == "text":

                print("\nDecomposition response:")
                print(block.text)

                task_plan = json.loads(block.text)

                print(
                    "\nTask plan type:",
                    type(task_plan)
                )

                print(
                    "Tasks type:",
                    type(task_plan["tasks"])
                )

                for task in task_plan["tasks"]:
                    print(
                        "Task Name:",
                        task.get("task_name")
                    )

                    print(
                        "Task Description:",
                        task.get("description")
                    )

                    print("------")

        if not task_plan:
            print("Task decomposition failed.")
            return

        # =================================================
        # 5. REMOVE STOP WORDS
        # =================================================

        query_words = {
            word
            for word in user_query.lower().split()
            if word not in STOP_WORDS
        }

        print("\nQuery words after stop-word removal:")
        print(query_words)

        # =================================================
        # 6. KEYWORD SEARCH
        # =================================================

        keyword_results = keyword_tool_search(
            user_query,
            TOOL_REGISTRY,
        )

        # =================================================
        # 7. SEMANTIC SEARCH
        # =================================================

        tool_text = [
            tool["search_text"]
            for tool in TOOL_REGISTRY
        ]

        tool_embeddings = embedding_model.encode(
            tool_text
        )

        query_embedding = embedding_model.encode(
            [user_query]
        )

        similarity = cosine_similarity(
            query_embedding,
            tool_embeddings,
        )[0]

        print("\nSemantic similarity scores:")

        for tool, score in zip(
            TOOL_REGISTRY,
            similarity,
        ):
            print(
                f"{tool['name']}: {score:.4f}"
            )

        # =================================================
        # 8. HYBRID TOOL SEARCH
        # =================================================

        hybrid_results = hybrid_tool_search(
            TOOL_REGISTRY,
            similarity,
            keyword_results,
        )

        print("\nHybrid search results:")

        for result in hybrid_results:
            print(
                result["tool"]["name"],
                "semantic:",
                result["semantic_score"],
                "keyword:",
                result["keyword_score"],
                "hybrid:",
                result["hybrid_score"],
            )

        # =================================================
        # 9. SELECT CANDIDATE TOOLS
        # =================================================

        selected_tools = select_candidate_tools(
            hybrid_results,
            threshhold=0.25,
        )

        print("\nCandidate tools:")

        for result in selected_tools:
            print(
                result["tool"]["name"],
                result["hybrid_score"],
            )

        # =================================================
        # 10. AUTHORIZATION FILTERING
        # =================================================

        authorized_tools = filter_authorized_tools(
            selected_tools,
            user_permissions,
        )

        print("\nAuthorized tools:")

        for result in authorized_tools:
            print(
                result["tool"]["name"],
                result["hybrid_score"],
            )

        # =================================================
        # 11. BUILD CLAUDE TOOLS
        # =================================================
        #
        # Important:
        # Claude receives only authorized tools.
        # We do not expose the complete TOOL_REGISTRY.
        # =================================================

        claude_tools = []

        for result in authorized_tools:

            tool = result["tool"]

            claude_tools.append(
                {
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "input_schema": tool.get("input_schema"),
                }
            )

        print("\nTools exposed to Claude:")

        for tool in claude_tools:
            print(tool)

        # =================================================
        # 12. ASK CLAUDE TO SELECT AND CALL TOOLS
        # =================================================

        tool_selection_response = await claude.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            tools=claude_tools,

            messages=[
                {
                    "role": "user",
                    "content": user_query,
                }
            ],
        )

        # =================================================
        # 13. COLLECT TOOL REQUESTS GENERICALLY
        # =================================================
        #
        # We do not create:
        #
        # status_input
        # balance_input
        # refund_input
        #
        # Instead, all tool requests are collected uniformly.
        # =================================================

        tool_requests = []

        for block in tool_selection_response.content:

            if block.type == "tool_use":

                tool_request = {
                    "tool_name": block.name,
                    "tool_input": block.input,
                }

                tool_requests.append(
                    tool_request
                )

                print("\nClaude requested tool:")
                print("Name:", block.name)
                print("Input:", block.input)

        print("\nAll tool requests:")

        for request in tool_requests:
            print(request)

        # =================================================
        # 14. APPLICATION VALIDATION
        # =================================================

        authorized_tool_names = {
            tool["name"]
            for tool in claude_tools
        }

        print("\nAuthorized tool names:")
        print(authorized_tool_names)

        for request in tool_requests:

            requested_tool_name = request["tool_name"]

            if requested_tool_name not in authorized_tool_names:

                print(
                    "\nBlocked unauthorized or unavailable tool:",
                    requested_tool_name,
                )

                return

        # =================================================
        # 15. CURRENT BUSINESS ORCHESTRATION
        # =================================================
        #
        # Current policy:
        # STATUS must be checked before BALANCE.
        #
        # We will generalize this section next.
        # =================================================

        status_request = find_tool_request(
            tool_requests,
            "get_customer_status",
        )

        balance_request = find_tool_request(
            tool_requests,
            "get_customer_balance",
        )

        refund_request = find_tool_request(
            tool_requests,
            "refund_customer",
        )

        # -------------------------------------------------
        # Execute STATUS first
        # -------------------------------------------------

        status_result_data = None

        if status_request:

            status_input = status_request["tool_input"]

            print("\n--- Executing STATUS first ---")

            status_tool_name = status_request["tool_name"]

            if not authorize_tool(
                status_tool_name,
                user_permissions,
            ):
                print(
                    "\n--- Authorization failed for STATUS ---"
                )
                return

            if not request_approval(
                status_tool_name,
                status_input,
            ):
                print(
                    "\n--- Approval denied for STATUS ---"
                )
                return

            status_response = await execute_mcp_tool(
                mcp_client,
                status_tool_name,
                status_input,
            )

            if not status_response["success"]:

                print("\n--- Status Check Failed ---")
                print(
                    "Error:",
                    status_response["error"],
                )

                return

            status_result = status_response["result"]

            print("\nStatus Result:")
            print(
                status_result.model_dump_json(
                    indent=2
                )
            )

            # ---------------------------------------------
            # Extract business payload from MCP response
            # ---------------------------------------------

            status_data = json.loads(
                status_result.content[0].text
            )

            if "error" in status_data:

                print("\n--- Status Check Failed ---")
                print(
                    "Error:",
                    status_data["error"],
                )

                print(
                    "\n--- Policy: Customer could not be "
                    "validated → dependent actions blocked ---"
                )

                return

            status_result_data = status_data

            status = status_data.get("status")

            print("\nCustomer status:", status)

        # -------------------------------------------------
        # Execute BALANCE only if customer is ACTIVE
        # -------------------------------------------------

        if balance_request:

            if not status_result_data:

                print(
                    "\n--- Balance blocked: status not checked ---"
                )
                return

            status = status_result_data.get("status")

            if status != "ACTIVE":

                print(
                    "\n--- Policy: Customer is not ACTIVE "
                    "→ Balance BLOCKED ---"
                )

                return

            balance_input = balance_request["tool_input"]

            print(
                "\n--- Policy: ACTIVE → Balance allowed ---"
            )

            balance_tool_name = balance_request["tool_name"]

            if not authorize_tool(
                balance_tool_name,
                user_permissions,
            ):
                print(
                    "\n--- Authorization failed for BALANCE ---"
                )
                return

            if not request_approval(
                balance_tool_name,
                balance_input,
            ):
                print(
                    "\n--- Approval denied for BALANCE ---"
                )
                return

            balance_response = await execute_mcp_tool(
                mcp_client,
                balance_tool_name,
                balance_input,
            )

            if not balance_response["success"]:

                print("\n--- Balance Check Failed ---")
                print(
                    "Error:",
                    balance_response["error"],
                )

                return

            print("\nBalance Result:")

            print(
                balance_response["result"].model_dump_json(
                    indent=2
                )
            )

        # -------------------------------------------------
        # Refund is intentionally not executed yet
        # -------------------------------------------------
        #
        # We will next design:
        #
        # STATUS → REFUND policy
        # refund amount validation
        # approval threshold
        # customer/entity binding
        # re-validation before execution
        # -------------------------------------------------

        if refund_request:

            print(
                "\nRefund request captured but not executed yet:"
            )

            print(refund_request)

            print(
                "\nNext step: implement safe refund orchestration."
            )


# =========================================================
# 16. MCP TOOL EXECUTION
# =========================================================

async def execute_mcp_tool(
    mcp_client,
    tool_name,
    tool_input,
):

    try:

        result = await mcp_client.call_tool(
            tool_name,
            tool_input,
        )

        return {
            "success": True,
            "result": result,
            "error": None,
        }

    except Exception as error:

        print(
            f"\nMCP Tool execution failed: {tool_name}"
        )

        print(
            "Technical error:",
            str(error),
        )

        return {
            "success": False,
            "result": None,
            "error": (
                "The service requested is currently "
                "unavailable. Please try again later."
            ),
        }


# =========================================================
# 17. AUTHORIZATION
# =========================================================

def authorize_tool(
    tool_name,
    user_permissions,
):

    required_permission = TOOL_PERMISSIONS.get(
        tool_name
    )

    if required_permission is None:
        return False

    return required_permission in user_permissions


# =========================================================
# 18. APPROVAL POLICY
# =========================================================

def requires_approval(
    tool_name,
    tool_input,
):

    policy = APPROVAL_POLICIES.get(
        tool_name
    )

    if not policy:
        return False

    amount = tool_input.get(
        policy["amount_field"]
    )

    return (
        amount is not None
        and amount > policy["approved_required_above"]
    )


def request_approval(
    tool_name,
    tool_input,
):

    if requires_approval(
        tool_name,
        tool_input,
    ):

        decision = input(
            f"Approval required for {tool_name} "
            f"with amount {tool_input.get('amount', 0)}. "
            "Approve? (yes/no): "
        )

        return decision.lower() == "yes"

    return True


# =========================================================
# 19. FIND TOOL REQUEST
# =========================================================

def find_tool_request(
    tool_requests,
    tool_name,
):

    for request in tool_requests:

        if request["tool_name"] == tool_name:
            return request

    return None


# =========================================================
# 20. KEYWORD TOOL SEARCH
# =========================================================

def keyword_tool_search(
    user_query,
    tool_registry,
):

    query = user_query.lower()

    matches = []

    query_words = set(
        query.split()
    )

    for tool in tool_registry:

        tool_words = set(
            tool["search_text"].lower().split()
        )

        overlap = query_words.intersection(
            tool_words
        )

        keyword_score = (
            len(overlap) / len(query_words)
            if query_words
            else 0
        )

        if overlap:

            matches.append(
                {
                    "tool": tool,
                    "matched_words": overlap,
                    "keyword_score": keyword_score,
                }
            )

    return matches


# =========================================================
# 21. HYBRID TOOL SEARCH
# =========================================================

def hybrid_tool_search(
    tool_registry,
    semantic_scores,
    keyword_results,
    semantic_weight=0.7,
    keyword_weight=0.3,
    top_k=3,
):

    keyword_scores = {
        result["tool"]["name"]: result["keyword_score"]
        for result in keyword_results
    }

    ranked_tools = []

    for tool, semantic_score in zip(
        tool_registry,
        semantic_scores,
    ):

        keyword_score = keyword_scores.get(
            tool["name"],
            0,
        )

        hybrid_score = (
            semantic_score * semantic_weight
            + keyword_score * keyword_weight
        )

        ranked_tools.append(
            {
                "tool": tool,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "hybrid_score": hybrid_score,
            }
        )

    ranked_tools.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True,
    )

    return ranked_tools[:top_k]


# =========================================================
# 22. SELECT CANDIDATE TOOLS
# =========================================================

def select_candidate_tools(
    ranked_tools,
    threshhold=0.25,
):

    candidate_tools = []

    for result in ranked_tools:

        hybrid_score = result["hybrid_score"]

        if hybrid_score > threshhold:

            candidate_tools.append(
                result
            )

    return candidate_tools


# =========================================================
# 23. FILTER AUTHORIZED TOOLS
# =========================================================

def filter_authorized_tools(
    ranked_tools,
    user_permissions,
):

    authorized_tools = []

    for result in ranked_tools:

        tool_name = result["tool"]["name"]

        if authorize_tool(
            tool_name,
            user_permissions,
        ):

            authorized_tools.append(
                result
            )

    return authorized_tools


# =========================================================
# 24. APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )