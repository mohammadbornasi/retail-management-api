from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )
    price: float = Field(
        ge=0
    )
    stock: int = Field(
        ge=0
    )


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    stock: int


class CustomerCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )
    email: str = Field(
        min_length=5,
        max_length=150
    )
    phone: str = Field(
        min_length=7,
        max_length=20
    )


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    

class OrderItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    item_total: float


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    total_price: float
    created_at: datetime
    status: OrderStatus
    items: list[OrderItemResponse]


class InventoryTransactionType(str, Enum):
    purchase = "purchase"
    sale = "sale"
    order_cancelled = "order_cancelled"
    adjustment = "adjustment"


class InventoryTransactionCreate(BaseModel):
    quantity: int
    transaction_type: InventoryTransactionType
    reason: str | None = Field(
        default=None,
        max_length=255,
    )


class InventoryTransactionResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    transaction_type: InventoryTransactionType
    reason: str | None
    created_at: datetime
