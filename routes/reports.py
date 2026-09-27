from datetime import date, datetime, time, timedelta, UTC

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Customer, Order, OrderItem, Product
from schemas import (
    SalesReportResponse,
    TopSellingProductsResponse,
    TopCustomersResponse,
    InventorySummaryResponse,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


SALES_STATUSES = {
    "confirmed",
    "processing",
    "shipped",
    "delivered",
}


@router.get("/sales/summary")
def get_sales_summary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Order).filter(
        Order.status.in_(SALES_STATUSES)
    )

    if from_date is not None:
        from_datetime = datetime.combine(
            from_date,
            time.min,
            tzinfo=UTC,
        )

        query = query.filter(
            Order.created_at >= from_datetime
        )

    if to_date is not None:
        to_datetime = datetime.combine(
            to_date,
            time.max,
            tzinfo=UTC,
        )

        query = query.filter(
            Order.created_at <= to_datetime
        )

    orders = query.all()

    total_orders = len(orders)

    total_sales = sum(
        order.total_price
        for order in orders
    )

    order_ids = [order.id for order in orders]

    if order_ids:
        total_items_sold = (
            db.query(func.sum(OrderItem.quantity))
            .filter(OrderItem.order_id.in_(order_ids))
            .scalar()
            or 0
        )
    else:
        total_items_sold = 0

    average_order_value = (
        round(total_sales / total_orders, 2)
        if total_orders
        else 0
    )

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "total_items_sold": total_items_sold,
    }


@router.get(
    "/sales",
    response_model=SalesReportResponse,
)
def get_sales_report(
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if from_date is None:
        from_date = date.today()

    if to_date is None:
        to_date = from_date

    if from_date > to_date:
        return {
            "items": [],
            "page": page,
            "limit": limit,
            "total": 0,
            "pages": 0,
        }

    start_datetime = datetime.combine(
        from_date,
        time.min,
        tzinfo=UTC,
    )

    end_datetime = datetime.combine(
        to_date,
        time.max,
        tzinfo=UTC,
    )

    rows = (
        db.query(
            func.date(Order.created_at).label("report_date"),
            func.sum(Order.total_price).label("total_sales"),
            func.count(Order.id).label("total_orders"),
        )
        .filter(
            Order.status.in_(SALES_STATUSES),
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
        )
        .group_by(
            func.date(Order.created_at)
        )
        .all()
    )

    sales_by_date = {
        row.report_date: {
            "total_sales": float(row.total_sales or 0),
            "total_orders": int(row.total_orders or 0),
        }
        for row in rows
    }

    all_days = []
    current_date = from_date

    while current_date <= to_date:
        data = sales_by_date.get(
            current_date.isoformat(),
            {
                "total_sales": 0,
                "total_orders": 0,
            },
        )

        all_days.append(
            {
                "date": current_date,
                "total_sales": data["total_sales"],
                "total_orders": data["total_orders"],
            }
        )

        current_date += timedelta(days=1)

    total = len(all_days)

    pages = (total + limit - 1) // limit if total else 0

    start = (page - 1) * limit
    end = start + limit

    items = all_days[start:end]

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


@router.get(
    "/products/top-selling",
    response_model=TopSellingProductsResponse,
)
def get_top_selling_products(
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.sum(OrderItem.quantity).label("quantity_sold"),
            func.sum(
                OrderItem.quantity * OrderItem.unit_price
            ).label("total_sales"),
        )
        .join(
            OrderItem,
            OrderItem.product_id == Product.id,
        )
        .join(
            Order,
            Order.id == OrderItem.order_id,
        )
        .filter(
            Order.status.in_(SALES_STATUSES)
        )
    )

    if from_date is not None:
        from_datetime = datetime.combine(
            from_date,
            time.min,
            tzinfo=UTC,
        )
        query = query.filter(
            Order.created_at >= from_datetime
        )

    if to_date is not None:
        to_datetime = datetime.combine(
            to_date,
            time.max,
            tzinfo=UTC,
        )
        query = query.filter(
            Order.created_at <= to_datetime
        )

    query = (
        query
        .group_by(
            Product.id,
            Product.name,
        )
        .order_by(
            func.sum(OrderItem.quantity).desc(),
            Product.id.asc(),
        )
    )

    results = query.all()

    total = len(results)

    pages = (
        (total + limit - 1) // limit
        if total
        else 0
    )

    offset = (page - 1) * limit

    paginated_results = results[
        offset:offset + limit
    ]

    items = [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity_sold": row.quantity_sold,
            "total_sales": round(row.total_sales, 2),
        }
        for row in paginated_results
    ]

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


@router.get(
    "/customers/top",
    response_model=TopCustomersResponse,
)
def get_top_customers(
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(
            Customer.id.label("customer_id"),
            Customer.name.label("customer_name"),
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_price).label("total_spent"),
        )
        .join(
            Order,
            Order.customer_id == Customer.id,
        )
        .filter(
            Order.status.in_(SALES_STATUSES)
        )
    )

    if from_date is not None:
        from_datetime = datetime.combine(
            from_date,
            time.min,
            tzinfo=UTC,
        )

        query = query.filter(
            Order.created_at >= from_datetime
        )

    if to_date is not None:
        to_datetime = datetime.combine(
            to_date,
            time.max,
            tzinfo=UTC,
        )

        query = query.filter(
            Order.created_at <= to_datetime
        )

    query = (
        query
        .group_by(
            Customer.id,
            Customer.name,
        )
        .order_by(
            func.sum(Order.total_price).desc(),
            Customer.id.asc(),
        )
    )

    results = query.all()

    total = len(results)

    pages = (
        (total + limit - 1) // limit
        if total
        else 0
    )

    offset = (page - 1) * limit

    paginated_results = results[
        offset:offset + limit
    ]

    items = [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "total_orders": int(row.total_orders),
            "total_spent": round(row.total_spent, 2),
        }
        for row in paginated_results
    ]

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


@router.get(
    "/inventory/summary",
    response_model=InventorySummaryResponse,
)
def get_inventory_summary(
    low_stock_threshold: int = Query(
        5,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    total_products = (
        db.query(func.count(Product.id))
        .scalar()
        or 0
    )

    total_stock = (
        db.query(func.sum(Product.stock))
        .scalar()
        or 0
    )

    total_inventory_value = (
        db.query(
            func.sum(
                Product.price * Product.stock
            )
        )
        .scalar()
        or 0
    )

    out_of_stock_products = (
        db.query(func.count(Product.id))
        .filter(Product.stock == 0)
        .scalar()
        or 0
    )

    low_stock_products = (
        db.query(func.count(Product.id))
        .filter(
            Product.stock <= low_stock_threshold
        )
        .scalar()
        or 0
    )

    return {
        "total_products": int(total_products),
        "total_stock": int(total_stock),
        "total_inventory_value": round(
            float(total_inventory_value),
            2,
        ),
        "out_of_stock_products": int(
            out_of_stock_products
        ),
        "low_stock_products": int(
            low_stock_products
        ),
    }