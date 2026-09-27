from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Customer
from schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerListResponse,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.email == customer.email)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="A customer with this email already exists",
        )

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@router.get("/", response_model=CustomerListResponse)
def get_customers(
    search: str | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (Customer.name.ilike(search_pattern))
            | (Customer.email.ilike(search_pattern))
            | (Customer.phone.ilike(search_pattern))
        )

    sort_columns = {
        "id": Customer.id,
        "name": Customer.name,
        "email": Customer.email,
        "phone": Customer.phone,
    }

    if sort_by not in sort_columns:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by. Allowed values: id, name, email, phone",
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

    customers = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    pages = ceil(total / limit) if total else 0

    return {
        "items": customers,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not existing_customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    email_exists = (
        db.query(Customer)
        .filter(
            Customer.email == customer.email,
            Customer.id != customer_id,
        )
        .first()
    )

    if email_exists:
        raise HTTPException(
            status_code=400,
            detail="A customer with this email already exists",
        )

    existing_customer.name = customer.name
    existing_customer.email = customer.email
    existing_customer.phone = customer.phone

    db.commit()
    db.refresh(existing_customer)

    return existing_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully"
    }
