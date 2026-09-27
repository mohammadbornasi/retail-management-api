from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ProductCreate, ProductResponse, ProductListResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)



@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        price=product.price,
        stock=product.stock,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product



@router.get("/", response_model=ProductListResponse)
def get_products(
    search: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_stock: int | None = Query(None, ge=0),
    max_stock: int | None = Query(None, ge=0),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_stock is not None:
        query = query.filter(Product.stock >= min_stock)

    if max_stock is not None:
        query = query.filter(Product.stock <= max_stock)

    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price",
            )

    if min_stock is not None and max_stock is not None:
        if min_stock > max_stock:
            raise HTTPException(
                status_code=400,
                detail="min_stock cannot be greater than max_stock",
            )

    sort_columns = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
        "stock": Product.stock,
    }

    if sort_by not in sort_columns:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by. Allowed values: id, name, price, stock",
        )

    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order. Allowed values: asc, desc",
        )

    sort_column = sort_columns[sort_by]

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()

    products = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    pages = ceil(total / limit) if total else 0

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


@router.get("/low-stock", response_model=list[ProductResponse])
def get_low_stock_products(
    threshold: int = 5,
    db: Session = Depends(get_db),
):
    return (
        db.query(Product)
        .filter(Product.stock <= threshold)
        .all()
    )



@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product



@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    existing_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.stock = product.stock

    db.commit()
    db.refresh(existing_product)

    return existing_product



@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }
