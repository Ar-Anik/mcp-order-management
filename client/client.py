import asyncio

from mcp import Client
from mcp.types import TextContent

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def main():

    async with Client(SERVER_URL) as client:

        print("\n=== SERVER INFO ===")

        print(client.server_info)
        print(client.protocol_version)
        print(client.server_capabilities)

        print("\n=== AVAILABLE TOOLS ===")

        tools_result = await client.list_tools()

        for tool in tools_result.tools:
            print(f"\nName: {tool.name}")
            print(f"Title: {tool.title}")
            print(f"Description: {tool.description}")
            print(f"Input schema: {tool.input_schema}")

        print("\n=== CALL get_product_tool ===")

        result = await client.call_tool(
            "get_product_tool",
            {
                "product_id": 1
            },
        )

        for content in result.content:

            if isinstance(content, TextContent):
                print(content.text)

        print("\n=== CALL get_customer_tool ===")

        result = await client.call_tool(
            "get_customer_tool",
            {
                "customer_id": 1
            },
        )

        for content in result.content:

            if isinstance(content, TextContent):
                print(content.text)

        print("\n=== CALL get_order_tool ===")

        result = await client.call_tool(
            "get_order_tool",
            {
                "order_id": 1
            },
        )

        for content in result.content:

            if isinstance(content, TextContent):
                print(content.text)

        print("\n=== READ RESOURCE ===")

        resource_result = await client.read_resource("order://1")

        for content in resource_result.contents:
            print(content)


        print("\n=== LIST PROMPTS ===")

        prompts_result = await client.list_prompts()

        for prompt in prompts_result.prompts:
            print(
                prompt.name,
                prompt.description,
            )

        print("\n=== CREATE ORDER ===")

        result = await client.call_tool(
            "create_order_tool",
            {
                "customer_id": 1,
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2,
                    },
                    {
                        "product_id": 2,
                        "quantity": 1,
                    },
                ],
            },
        )

        for content in result.content:

            if isinstance(content, TextContent):
                print(content.text)


        print("\n=== UPDATE ORDER STATUS ===")

        result = await client.call_tool(
            "update_order_status_tool",
            {
                "order_id": 1,
                "status": "shipped",
            },
        )

        for content in result.content:

            if isinstance(content, TextContent):
                print(content.text)


        print("\n=== call analyze_order ===")

        prompt_result = await client.get_prompt(
            'analyze_order',
            {
                'order_id': '1'
            },
        )

        print(prompt_result)


if __name__ == "__main__":
    asyncio.run(main())
