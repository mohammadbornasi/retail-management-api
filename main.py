from fastapi import FastAPI
from database import Base, engine
from models import Product
from routes.products import router as products_router
from routes.customers import router as customers_router
from routes.orders import router as orders_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Retail Management API",
    description="A practical retail management REST API",
    version="1.0.0",
)

app.include_router(products_router)
app.include_router(customers_router)
app.include_router(orders_router)

@app.get("/")
def root():
    return {
        "message": "Retail Management API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }