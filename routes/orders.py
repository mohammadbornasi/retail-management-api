from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Customer, Order, OrderItem, Product
from schemas import OrderCreate, OrderResponse, OrderStatus, OrderItemCreate, OrderItemUpdate

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
):
    # Check customer
    customer = (
        db.query(Customer)
        .filter(Customer.id == order.customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # Check that order has at least one item
    if not order.items:
        raise HTTPException(
            status_code=400,
            detail="Order must contain at least one item",
        )

    # Check products and stock
    products = {}

    for item in order.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found",
            )

        products[item.product_id] = product

    # Create order
    new_order = Order(
        customer_id=order.customer_id,
        total_price=0,

    )

    db.add(new_order)
    db.flush()

    # Create order items and update stock
    total_price = 0

    for item in order.items:
        product = products[item.product_id]

        unit_price = product.price
        item_total = unit_price * item.quantity

        total_price += item_total

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
        )

        db.add(order_item)


    # Save final order total
    new_order.total_price = total_price

    db.commit()
    db.refresh(new_order)

    return {
        "order_id": new_order.id,
        "customer_id": new_order.customer_id,
        "total_price": new_order.total_price,
        "created_at": new_order.created_at,
        "status": new_order.status,
        "message": "Order created successfully",
    }


ALLOWED_STATUS_TRANSITIONS = {
    OrderStatus.pending.value: {
        OrderStatus.confirmed.value,
        OrderStatus.cancelled.value,
    },
    OrderStatus.confirmed.value: {
        OrderStatus.processing.value,
        OrderStatus.cancelled.value,
    },
    OrderStatus.processing.value: {
        OrderStatus.shipped.value,
    },
    OrderStatus.shipped.value: {
        OrderStatus.delivered.value,
    },
    OrderStatus.delivered.value: set(),
    OrderStatus.cancelled.value: set(),
}


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
):
    try:
        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        current_status = order.status

        if current_status == new_status.value:
            raise HTTPException(
                status_code=400,
                detail=f"Order is already {current_status}",
            )

        allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status.value not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change order status "
                    f"from {current_status} to {new_status.value}"
                ),
            )

        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order_id)
            .all()
        )

        if (
            current_status == OrderStatus.pending.value
            and new_status == OrderStatus.confirmed
        ):
            products = {}

            for item in order_items:
                product = (
                    db.query(Product)
                    .filter(Product.id == item.product_id)
                    .first()
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found",
                    )

                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Not enough stock for product {product.id}. "
                            f"Available: {product.stock}, "
                            f"requested: {item.quantity}"
                        ),
                    )

                products[item.product_id] = product

            for item in order_items:
                product = products[item.product_id]
                product.stock -= item.quantity

            order.status = OrderStatus.confirmed.value

        elif (
            current_status == OrderStatus.confirmed.value
            and new_status == OrderStatus.cancelled
        ):
            for item in order_items:
                product = (
                    db.query(Product)
                    .filter(Product.id == item.product_id)
                    .first()
                )

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_id} not found",
                    )

                product.stock += item.quantity

            order.status = OrderStatus.cancelled.value

        else:
            order.status = new_status.value

        db.commit()
        db.refresh(order)

        items = []

        for item in order_items:
            items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "item_total": item.unit_price * item.quantity,
                }
            )

        return {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "status": order.status,
            "items": items,
            "message": f"Order status updated to {order.status}",
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise
    


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    items = []

    for item in order_items:
        items.append(
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "item_total": item.unit_price * item.quantity,
            }
        )

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "items": items,
        "status": order.status,
    }


@router.post("/{order_id}/items")
def create_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status != OrderStatus.pending.value:
        raise HTTPException(
            status_code=400,
            detail="Items can only be added to pending orders",
        )

    product = (
        db.query(Product)
        .filter(Product.id == item_data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product {item_data.product_id} not found",
        )

    existing_item = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product.id,
        )
        .first()
    )

    if existing_item:
        existing_item.quantity += item_data.quantity
        order_item = existing_item
    else:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=product.price,
        )
        db.add(order_item)

    db.flush()

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    order.total_price = sum(
        item.quantity * item.unit_price
        for item in order_items
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order_item)
    db.refresh(order)

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_price": order.total_price,
        "status": order.status,
        "product_id": order_item.product_id,
        "quantity": order_item.quantity,
        "unit_price": order_item.unit_price,
        "item_total": order_item.quantity * order_item.unit_price,
        "message": "Order item added successfully",
    }




@router.delete("/{order_id}/items/{product_id}")
def delete_order_item(
    order_id: int,
    product_id: int,
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status != OrderStatus.pending.value:
        raise HTTPException(
            status_code=400,
            detail="Items can only be deleted from pending orders",
        )

    order_item = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product_id,
        )
        .first()
    )

    if not order_item:
        raise HTTPException(
            status_code=404,
            detail="Order item not found",
        )

    db.delete(order_item)
    db.flush()

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    order.total_price = sum(
        item.quantity * item.unit_price
        for item in order_items
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_price": order.total_price,
        "status": order.status,
        "message": "Order item deleted successfully",
    }



@router.patch("/{order_id}/items/{product_id}")
def update_order_item(
    order_id: int,
    product_id: int,
    item_data: OrderItemUpdate,
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status != OrderStatus.pending.value:
        raise HTTPException(
            status_code=400,
            detail="Items can only be updated in pending orders",
        )

    order_item = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product_id,
        )
        .first()
    )

    if not order_item:
        raise HTTPException(
            status_code=404,
            detail="Order item not found",
        )

    order_item.quantity = item_data.quantity

    db.flush()

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    order.total_price = sum(
        item.quantity * item.unit_price
        for item in order_items
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order_item)
    db.refresh(order)

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_price": order.total_price,
        "status": order.status,
        "product_id": order_item.product_id,
        "quantity": order_item.quantity,
        "unit_price": order_item.unit_price,
        "item_total": order_item.quantity * order_item.unit_price,
        "message": "Order item updated successfully",
    }
