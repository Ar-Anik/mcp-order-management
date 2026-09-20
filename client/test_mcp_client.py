import asyncio

from mcp import Client


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    async with Client(MCP_SERVER_URL) as client:

        result = await client.list_tools()

        print("\nAvailable MCP tools:\n")

        for tool in result.tools:
            print(tool)
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Input schema: {tool.input_schema}")
            print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
