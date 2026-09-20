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
