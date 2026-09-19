from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas import ProductResult


async def get_product(session: AsyncSession, product_id: int) -> ProductResult | None:

    result = await session.execute(
        select(Product).where(
            Product.id == product_id
        )
    )

    product = result.scalar_one_or_none()

    if product is None:
        return None

    return ProductResult(
        id=product.id,
        name=product.name,
        price=product.price,
        stock=product.stock,
    )


async def search_products(session: AsyncSession, query: str) -> list[ProductResult]:

    result = await session.execute(
        select(Product)
        .where(Product.name.ilike(f"%{query}%"))
        .order_by(Product.id)
    )

    products = result.scalars().all()

    return [
        ProductResult(
            id=product.id,
            name=product.name,
            price=product.price,
            stock=product.stock,
        )
        for product in products
    ]

