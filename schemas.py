from pydantic import BaseModel, Field


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
    id: int
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True


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
    id: int
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True