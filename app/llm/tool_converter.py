"""
MCP Server-এর tool definition Gemini বুঝবে এমন function declaration-এ convert করতে হবে।

MCP Server থেকে tool আসবে:
- name
- description
- input_schema

Gemini চায়:
- name
- description
- parameters
"""

from typing import Any
from google.genai import types

# JSON Schema fields that should not be passed to Gemini
UNSUPPORTED_KEYS = {
    "additionalProperties",
    "additional_properties",
    "$schema",
    "$defs",
    "definitions",
}

"""
ধরা যাক MCP থেকে schema এসেছে:
schema = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False
            }
        }
    }
}

Gemini additionalProperties accept করছে না। তাই আগে বলে দিতে হবে:

UNSUPPORTED_KEYS = {
    "additionalProperties",
}

এর অর্থ, এই নামের key পাওয়া গেলে schema থেকে বাদ দিতে হবে। এটা শুধু একটি list/set of forbidden keys।
"""


"""
UNSUPPORTED_KEYS শুধু জানে কোন key remove করতে হবে কিন্তু জানে না schema-এর কোথায় key-টা আছে
তাই normalize_schema() দরকার।
"""

def normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Convert MCP/JSON Schema into a Gemini-compatible schema.
    """

    if not isinstance(schema, dict):
        return schema

    result = {}

    for key, value in schema.items():

        # Remove unsupported JSON Schema fields
        if key in UNSUPPORTED_KEYS:
            continue

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            result[key] = normalize_schema(value)

        # Recursively process arrays
        elif isinstance(value, list):
            result[key] = [
                normalize_schema(item)
                if isinstance(item, dict)
                else item
                for item in value
            ]

        else:
            result[key] = value

    return result

"""
-> normalize_schema()
এটা পুরো schema-এর ভিতর recursively search করে।

MCP Schema
   │
   ├── type
   │
   ├── properties
   │      │
   │      └── items
   │            │
   │            └── array items
   │                   │
   │                   └── additionalProperties ❌
   │
   └── required

JSON Schema nested হতে পারে। additionalProperties শুধু top-level-এ থাকবে এমন নয়; properties, items, বা আরও nested object-এর ভিতরেও থাকতে পারে। normalize_schema() প্রতিটি nested dictionary এবং list-এর ভিতরে গিয়ে একইভাবে schema clean করে।
"""

"""
Problem: Tool like, create_order_tool:

create_order_tool(
    customer_id: int,
    items: list[...]
)

এখানে items হলো list/array।

object
├── customer_id → integer
└── items       → array
                  │
                  ├── item 1 → object
                  ├── item 2 → object
                  └── item 3 → object

customer_id একটি simple integer। কিন্তু items একটি array, এবং array-এর প্রতিটি element একটি structured object। তাই items-এর schema naturally বেশি complex এবং nested।
"""

"""
create_order_tool define করা:

async def create_order_tool(customer_id: int, items: list[OrderItem]):
    pass

    
"""

def mcp_tool_to_gemini_function(tool: Any):
    parameters = normalize_schema(tool.input_schema)

    return {
        "name": tool.name,
        "description": tool.description or '',
        "parameters": parameters,
    }

def create_gemini_tools(mcp_tools: list[Any]):
    function_declarations = [
        mcp_tool_to_gemini_function(tool)
        for tool in mcp_tools
    ]

    return [
        types.Tool(
            function_declarations=function_declarations
        )
    ]

"""
MCP SDK-এর list_tools() result-এ tool-এর name, description এবং input_schema থাকে।
"""
