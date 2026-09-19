from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Customer, Order, OrderItem, Product

from app.schemas import CreateOrderInput, OrderItemResult, OrderResult

async def get_order(session: AsyncSession, order_id: int) -> OrderResult:
    result = await session.execute(
        select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if order is None:
        return None

    return OrderResult(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            OrderItemResult(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_pricce,
            )
            for item in order.items
        ]
    )


async def create_order(session: AsyncSession, data: CreateOrderInput) -> OrderResult:

    customer_result = await session.execute(
        select(Customer).where(
            Customer.id == data.customer_id
        )
    )

    customer = customer_result.scalar_one_or_none()

    if customer is None:
        raise ValueError("Customer not found.")

    product_ids = [
        item.product_id
        for item in data.items
    ]

    product_result = await session.execute(
        select(Product).where(
            Product.id.in_(product_ids)
        )
    )

    products = {
        product.id: product
        for product in product_result.scalars().all()
    }

    if len(products) != len(set(product_ids)):
        raise ValueError(
            "One or more products were not found."
        )

    total = Decimal("0")

    order = Order(
        customer_id=data.customer_id,
        status="pending",
        total_amount=Decimal("0"),
    )

    session.add(order)

    for item_input in data.items:

        product = products[item_input.product_id]

        if product.stock < item_input.quantity:
            raise ValueError(
                f"Insufficient stock for product "
                f"{product.name}."
            )

        item_total = (
            product.price * item_input.quantity
        )

        total += item_total

        product.stock -= item_input.quantity

        order_item = OrderItem(
            product=product,
            quantity=item_input.quantity,
            unit_price=product.price,
        )

        order.items.append(order_item)

    order.total_amount = total

    await session.commit()

    return await get_order(session, order.id)


async def update_order_status(session: AsyncSession, order_id: int, status: str) -> OrderResult:
    allowed_statuses = {
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled",
    }

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid status: {status}"
        )

    result = await session.execute(
        select(Order).where(
            Order.id == order_id
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise ValueError("Order not found.")

    order.status = status

    await session.commit()

    result = await get_order(session, order_id)

    if result is None:
        raise ValueError("Order not found.")

    return result

