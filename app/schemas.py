from decimal import Decimal
from pydantic import BaseModel, Field


class CustomerResult(BaseModel):
    id: int
    name: str
    email: str


class ProductResult(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int


class OrderItemInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class CreateOrderInput(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemInput] = Field(min_length=1)


class OrderItemResult(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderResult(BaseModel):
    id: int
    customer_id: int
    status: str
    total_amount: Decimal
    items: list[OrderItemResult]
