from typing import Any

from google.genai import types
from mcp import Client

from .gemini import client
from .tool_converter import create_gemini_tools

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"

MODEL_NAME = 'gemini-3.7-flash'


class MCPAgent:
    def __init__(self, mcp_client: Client):
        self.mcp_client = mcp_client


    async def get_mcp_tools(self):
        result = await self.mcp_client.list_tools()

        return result.tools

    async def run(self, user_message: str):
        mcp_tools = await self.get_mcp_tools()

        # import pdb; pdb.set_trace()
        gemini_tools = create_gemini_tools(mcp_tools)

        """
        এখানে Gemini-কে পাঠানোর conversation content তৈরি হচ্ছে।
        
        যদি: user_message = "Find customer 10"
        তাহলে structure হচ্ছে:
        
            contents
               ↓
            User message
               ↓
            "Find customer 10"
        
        সহজভাবে, contents = Gemini-কে পাঠানোর conversation/message data।
        """
        contents: list[Any] = [
            types.Content(
                role='user',
                parts=[
                    types.Part(text=user_message)
                ]
            )
        ]

        """
        - এখানে types.Content হলো Google Gemini SDK-এর একটি class/type।
        - types.Part(...) হলো Content-এর ভিতরের একটি Part object।
        """

        config = types.GenerateContentConfig(tools=gemini_tools)
        """
        এখানে Gemini-কে জানানো হচ্ছে:
        এই tools-গুলো available আছে; প্রয়োজন হলে এগুলো call করার জন্য function call তৈরি করা যাবে।
        """

        while True:

            """
            এটা Gemini API call। এখানে তিনটি প্রধান জিনিস যাচ্ছে:
            model
              ↓
            কোন Gemini model ব্যবহার হবে

            contents
              ↓
            User কী বলেছে

            config
              ↓
            কোন tools Gemini ব্যবহার করতে পারবে
            """
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )
            """
            তারপর Gemini response দেয়:
            Gemini
               ↓
            response

            এই response-এর মধ্যে Gemini হয় Final text দেবে অথবা Function/tool call দেবে।
            """
            # import pdb
            # pdb.set_trace()
            """
            Gemini কোনো candidate response দিয়েছে কি না check করছে। না দিলে function এখানেই শেষ।
            """
            if not response.candidates:
                return "No Responsee was Generated."
            """
            response.candidates মানে হলো Gemini যে সম্ভাব্য response/output গুলো দিয়েছে, সেগুলোর list।
            """

            model_content = response.candidates[0].content
            """
            Gemini-এর প্রথম response-এর content নেওয়া হচ্ছে। এতে থাকতে পারে: normal text অথবা tool/function call
            """

            contents.append(model_content)
            """
            Gemini কী response দিয়েছে সেটা conversation history-তে রাখা হচ্ছে। পরের Gemini request-এর সময় আগের response-টাও context হিসেবে থাকবে।
            """

            function_calls = response.function_calls
            """
            Gemini কোনো MCP tool call করতে বলেছে কি না বের করা হচ্ছে।
            """

            if not function_calls:
                return response.text or 'No Text Response was Generated.'
            """
            Tool call নেই মানে Gemini সরাসরি final text answer দিয়েছে। তাই সেই text return করা হচ্ছে।
            """

            for function_call in function_calls:
                tool_name = function_call.name
                tool_arguments = function_call.args or {}

                print(
                    f"\n[LLM requested tool]"
                    f"\nTool: {tool_name}"
                    f"\nArguments: {tool_arguments}\n"
                )

                tool_result = await self.mcp_client.call_tool(tool_name, tool_arguments)

                """
                Error হলে Gemini-কে জানানোর জন্য error information তৈরি হচ্ছে।
                """
                if tool_result.is_error:
                    result_data = {
                        "error": True,
                        "message": str(tool_result.content),
                    }
                else:
                    """
                    Tool successfully execute হলে তার structured result নেওয়া হচ্ছে। যেমন:
                    {
                        "id": 10,
                        "name": "John",
                        "email": "john@example.com"
                    }
                    """
                    result_data = {
                        "error": False,
                        "result": tool_result.structured_content,
                    }

                    """
                    যদি structured_content না থাকে, তাহলে সাধারণ content থেকে result নেওয়া হচ্ছে।
                    """
                    if result_data["result"] is None:
                        result_data["result"] = [
                            getattr(item, 'model_dump', lambda: str(item))()
                            for item in tool_result.content
                        ]

                """
                MCP Tool থেকে পাওয়া result-কে Gemini বুঝতে পারে এমন function response হিসেবে তৈরি করা হচ্ছে।
                """
                function_response_part = (
                    types.Part.from_function_response(
                        name=tool_name,
                        response=result_data,
                    )
                )

                """
                Tool-এর result conversation history-তে যোগ করা হচ্ছে।
                """
                contents.append(
                    types.Content(
                        role='user',
                        parts=[function_response_part],
                    )
                )



