from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
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


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    limit: int
    total: int
    pages: int


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


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    page: int
    limit: int
    total: int
    pages: int


class OrderListItem(BaseModel):
    order_id: int
    customer_id: int
    total_price: float
    created_at: datetime
    status: OrderStatus


class OrderListResponse(BaseModel):
    items: list[OrderListItem]
    page: int
    limit: int
    total: int
    pages: int


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


class SalesReportItem(BaseModel):
    date: date
    total_sales: float
    total_orders: int


class SalesReportResponse(BaseModel):
    items: list[SalesReportItem]
    page: int
    limit: int
    total: int
    pages: int


class TopSellingProductItem(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    total_sales: float


class TopSellingProductsResponse(BaseModel):
    items: list[TopSellingProductItem]
    page: int
    limit: int
    total: int
    pages: int


class TopCustomerItem(BaseModel):
    customer_id: int
    customer_name: str
    total_orders: int
    total_spent: float


class TopCustomersResponse(BaseModel):
    items: list[TopCustomerItem]
    page: int
    limit: int
    total: int
    pages: int


class InventorySummaryResponse(BaseModel):
    total_products: int
    total_stock: int
    total_inventory_value: float
    out_of_stock_products: int
    low_stock_products: int


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: str = Field(
        min_length=5,
        max_length=150,
    )

    password: str = Field(
        min_length=8,
        max_length=100,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str