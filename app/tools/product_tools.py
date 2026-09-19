from mcp.server import MCPServer
from app.database import SessionLocal
from app.services.product_service import get_product, search_products

def register_product_tools(mcp: MCPServer):

    @mcp.tool()
    async def get_product_tool(product_id: int):

        async with SessionLocal() as session:
            product = await get_product(session, product_id)

            if product is None:
                return {
                    "error": "Product not found",
                }

            return product.model_dump()


    @mcp.tool()
    async def search_products_tool(query: str):

        async with SessionLocal() as session:
            products = await search_products(session, query)

            return [
                product.model_dump()
                for product in products
            ]

