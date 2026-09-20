import asyncio
from mcp import Client
from .agent import MCPAgent

MCP_SERVER_URL = 'http://127.0.0.1:8000/mcp'

async def main():

    async with Client(MCP_SERVER_URL) as client:
        agent = MCPAgent(client)

        print("MCP + Gemini Chat")
        print("Type 'exit' to quit.\n")

        while True:
            user_message = input('User: ').strip()

            if user_message.lower() == 'exit':
                break

            if not user_message:
                continue

            try:
                answer = await agent.run(user_message)

                print(f"\nAssistant: {answer}\n")

            except Exception as e:
                print(f"\nError: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
