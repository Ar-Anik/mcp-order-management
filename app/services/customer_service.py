from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer
from app.schemas import CustomerResult

async def get_customer(session: AsyncSession, customer_id: int) -> CustomerResult|None:
    result = await session.execute(
        select(Customer).where(
            Customer.id == customer_id
        )
    )

    customer = result.scalar_one_or_none()

    if customer is None:
        return None

    return CustomerResult(
        id=customer.id,
        name=customer.name,
        email=customer.email,
    )


async def search_customers(session: AsyncSession, query: str) -> list[CustomerResult]:
    result = await session.execute(
        select(Customer).where(
            Customer.name.ilike(f'%{query}%').order_by(
                Customer.id
            )
        )
    )

    customers = result.scalars().all()

    return [
        CustomerResult(
            id=customer.id,
            name=customer.name,
            email=customer.email,
        )
        for customer in customers
    ]

