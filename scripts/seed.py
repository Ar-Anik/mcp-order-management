import asyncio
from decimal import Decimal

from app.database import SessionLocal, create_tables
from app.models import Customer, Product


async def seed():

    await create_tables()

    async with SessionLocal() as session:

        customer1 = Customer(
            name="Alice Rahman",
            email="alice@example.com",
        )

        customer2 = Customer(
            name="Bob Hasan",
            email="bob@example.com",
        )

        product1 = Product(
            name="Mechanical Keyboard",
            price=Decimal("85.00"),
            stock=20,
        )

        product2 = Product(
            name="Wireless Mouse",
            price=Decimal("35.00"),
            stock=50,
        )

        product3 = Product(
            name="USB-C Hub",
            price=Decimal("45.00"),
            stock=30,
        )

        session.add_all(
            [
                customer1,
                customer2,
                product1,
                product2,
                product3,
            ]
        )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
