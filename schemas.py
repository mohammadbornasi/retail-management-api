from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True