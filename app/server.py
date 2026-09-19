import json
import asyncio
from mcp.server import MCPServer
from pygments.lexers import web

from app.database import create_tables, SessionLocal
from app.services.order_service import get_order
from app.tools.customer_tools import register_customer_tools
from app.tools.order_tools import register_order_tools
from app.tools.product_tools import register_product_tools

mcp = MCPServer(
    'Order Management MCP Server',
    version='1.0',
    instructions=(
        "Use the available order management tools "
        "to retrieve and manage customers, products, "
        "and orders."
    ),
)

register_customer_tools(mcp)
register_order_tools(mcp)
register_product_tools(mcp)


"""
order://{order_id} -> একটি URI, it define resource like : 
order://{order_id}
        ↓
order://10025
order://10026
order://10027
order://20050
...

এগুলো আলাদা আলাদা resource address।
"""

@mcp.resource('order://{order_id}', mime_type='application/json')
async def order_resource(order_id: str):

    async with SessionLocal() as session:
        order = await get_order(session, int(order_id))

        if order is None:
            return json.dumps({'error': 'order not found'})

        return order.model_dump()


"""
Create a prompt for analyzing an order.
"""

@mcp.prompt()
def analyze_order(order_id: str):
    return (
        f"Analyze order {order_id}. "
        "Explain its current status, total amount, "
        "items, and any useful observations."
    )


"""
transport='streamable-http' -> MCP server-কে Streamable HTTP transport দিয়ে চালু করো।

transport এখানে বলে MCP client এবং MCP server-এর মধ্যে protocol messages কীভাবে যাতায়াত করবে। Current SDK documentation অনুযায়ী streamable-http একটি 
real HTTP server চালায়; default endpoint হলো /mcp এবং default host/port 127.0.0.1:8000।
"""

if __name__ == '__main__':
    asyncio.run(create_tables())

    mcp.run(
        transport='streamable-http'
    )

"""
3 Layer of MCP : 
- MCP Protocol
- Transport
- Tool / Resource

Current official Python SDK-তেও এই separation-টাই করা হয়েছে। stdio এবং streamable-http transport দুটোই MCP messages বহন করতে পারে।
"""

"""
ধরা যাক একটি AI application আছে:

  AI Application
      ↓
   MCP Client
      ↓
   MCP Server
      ↓
   PostgreSQL

MCP Client-এর কাজ হলো MCP Server-এর সাথে MCP protocol অনুযায়ী কথা বলা। MCP Server-এর কাজ হলো tools/resources expose করা।

যেমন server-এর কাছে আছে:
get_customer
search_customers
get_order
create_order

কিন্তু Client এবং Server কীভাবে নিজেদের মধ্যে message পাঠাবে? এখানেই transport আসে।
"""

"""
MCP Protocol হলো দুই পক্ষের মধ্যে communication-এর rules। উদাহরণ:

Client বলতে পারে: "Server-এর available tools কী কী?"
এটি MCP-এর একটি defined operation।

Server উত্তর দেয়: "এই tools available..."

আবার Client বলতে পারে: "get_customer tool চালাও, customer_id = 10"

Server সেই tool execute করে result ফেরত দেয়।

Conceptually:

    MCP Client
        │
        │ MCP message
        ↓
    MCP Server
        │
        │ MCP message
        ↓
    MCP Client

MCP protocol-এর message format JSON-RPC-এর উপর ভিত্তি করে। কিন্তু JSON-RPC message কীভাবে Client থেকে Server-এ যাবে, সেটা transport-এর দায়িত্ব।
"""

"""
Transport হলো খুব সহজভাবে:
    MCP message এক জায়গা থেকে আরেক জায়গায় যাওয়ার communication mechanism।

দুটি প্রধান transport:

MCP Protocol
     │
     ├── STDIO
     │
     └── Streamable HTTP

Official Python SDK-তে mcp.run()-এর default transport হলো stdio; streamable-http দিলে একটি HTTP server চালু হয়
"""
