from mcp.server import MCPServer

from app.database import SessionLocal
from app.schemas import CreateOrderInput
from app.services.order_service import create_order, get_order, update_order_status


def register_order_tools(mcp: MCPServer) -> None:

    @mcp.tool()
    async def get_order_tool(order_id: int):

        async with SessionLocal() as session:

            order = await get_order(session, order_id)

            if order is None:
                return {
                    "error": "Order not found."
                }

            return order.model_dump()


    @mcp.tool()
    async def create_order_tool(customer_id: int, items: list[dict]):

        data = CreateOrderInput(
            customer_id=customer_id,
            items=items,
        )

        async with SessionLocal() as session:
            order = await create_order(session, data)

            return order.model_dump()


    @mcp.tool()
    async def update_order_status_tool(order_id: int, status: str):

        async with SessionLocal() as session:
            order = await update_order_status(session, order_id, status)

            return order.model_dump()

