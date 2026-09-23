from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product, InventoryTransaction
from schemas import (
    InventoryTransactionCreate,
    InventoryTransactionResponse,
)

router = APIRouter(
    prefix="/products",
    tags=["Inventory"],
)


@router.post(
    "/{product_id}/inventory",
    response_model=InventoryTransactionResponse,
)
def create_inventory_transaction(
    product_id: int,
    transaction: InventoryTransactionCreate,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if transaction.quantity == 0:
        raise HTTPException(
            status_code=422,
            detail="Quantity cannot be zero",
        )

    if transaction.quantity < 0:
        decrease_amount = abs(transaction.quantity)

        if decrease_amount > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock",
            )

    product.stock += transaction.quantity

    inventory_transaction = InventoryTransaction(
        product_id=product_id,
        quantity=transaction.quantity,
        transaction_type=transaction.transaction_type,
        reason=transaction.reason,
    )

    db.add(inventory_transaction)

    try:
        db.commit()
        db.refresh(inventory_transaction)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create inventory transaction",
        )

    return inventory_transaction


@router.get(
    "/{product_id}/inventory",
    response_model=list[InventoryTransactionResponse],
)
def get_inventory_transactions(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    transactions = (
        db.query(InventoryTransaction)
        .filter(
            InventoryTransaction.product_id == product_id
        )
        .order_by(
            InventoryTransaction.created_at.desc()
        )
        .all()
    )

    return transactions