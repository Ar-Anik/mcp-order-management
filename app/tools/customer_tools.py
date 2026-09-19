from mcp.server import MCPServer
from app.database import SessionLocal
from app.services.customer_service import get_customer, search_customers

def register_customer_tools(mcp:MCPServer):

    """
    - mcp: MCPServer, এখানে mcp সাধারণত MCP server application-এর main object
    এর কাজ হলো MCP server-এর capabilities manage করা।

    - @mcp.tool() এটি একটি decorator।
    decorator-এর উদ্দেশ্য হলো Python function-টিকে MCP server-এর একটি Tool হিসেবে register করা।

    SDK function name, docstring এবং type hints ব্যবহার করে tool-এর metadata এবং input schema তৈরি করে।
    """

    @mcp.tool()
    async def get_customer_tool(customer_id: int):

        async with SessionLocal() as session:
            customer = await get_customer(session, customer_id)

            if customer is None:
                return {
                    "error": "customer not found",
                }

            return customer.model_dump()

    @mcp.tool()
    async def search_customers_tool(query: str):
        async with SessionLocal() as session:
            customers = await search_customers(session, query)

            return [
                customer.model_dump()
                for customer in customers
            ]
