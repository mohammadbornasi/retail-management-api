# Retail Management API

A practical REST API for managing products, customers, orders, and inventory, built with Python and FastAPI.

## About the Project

Retail Management API is a backend application designed as a foundation for a retail management system.

The project demonstrates how to build a RESTful API with:

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Alembic
* Automated testing

The application currently supports product and customer management, order creation and management, order status workflows, and inventory adjustments based on order status.

The project is being developed incrementally with a focus on clean API design, database integration, business logic, testing, and maintainability.

## Current Features

### Product Management

* Create products
* List all products
* Retrieve a product by ID
* Update products
* Delete products
* Manage product prices and stock

### Customer Management

* Create customers
* List all customers
* Retrieve a customer by ID
* Update customers
* Delete customers
* Prevent duplicate customer emails

### Order Management

* Create orders for customers
* Add products to orders
* Update order item quantities
* Delete order items
* Retrieve complete order details
* Calculate order totals
* Snapshot product prices when items are added to an order

### Order Status Workflow

Orders support the following statuses:

```text
pending
   ├── confirmed
   │      ├── processing
   │      │      └── shipped
   │      │             └── delivered
   │      └── cancelled
   │
   └── cancelled
```

The API validates allowed status transitions.

When an order changes from `pending` to `confirmed`, the required product stock is deducted.

When a confirmed order is cancelled, the reserved stock is restored.

### Database

* SQLite database
* SQLAlchemy ORM
* Alembic database migrations
* Product, customer, order, and order item models

### Testing

The project includes an automated test suite covering:

* Product endpoints
* Customer endpoints
* Order creation and retrieval
* Order item management
* Order status transitions
* Inventory changes
* Validation and error handling
* API health endpoints

Current test status:

```text
61 tests passed
98% overall code coverage
```

## Technologies

* Python 3.14
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Alembic
* Uvicorn
* Pytest
* Coverage.py
* Git & GitHub

## Project Structure

```text
retail-management-api/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── ...
│
├── routes/
│   ├── customers.py
│   ├── orders.py
│   └── products.py
│
├── tests/
│   ├── conftest.py
│   ├── test_customers.py
│   ├── test_health.py
│   ├── test_orders.py
│   └── test_products.py
│
├── database.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── .gitignore
└── README.md
```

The SQLite database, virtual environment, and test coverage artifacts are excluded from version control using `.gitignore`.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mohammadbornasi/retail-management-api.git
```

### 2. Navigate to the project

```bash
cd retail-management-api
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the API

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

## API Endpoints

### Products

| Method | Endpoint         | Description      |
| ------ | ---------------- | ---------------- |
| POST   | `/products/`     | Create a product |
| GET    | `/products/`     | Get all products |
| GET    | `/products/{id}` | Get a product    |
| PUT    | `/products/{id}` | Update a product |
| DELETE | `/products/{id}` | Delete a product |

### Customers

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| POST   | `/customers/`              | Create a customer |
| GET    | `/customers/`              | Get all customers |
| GET    | `/customers/{customer_id}` | Get a customer    |
| PUT    | `/customers/{customer_id}` | Update a customer |
| DELETE | `/customers/{customer_id}` | Delete a customer |

### Orders

| Method | Endpoint                                | Description             |
| ------ | --------------------------------------- | ----------------------- |
| POST   | `/orders/`                              | Create an order         |
| GET    | `/orders/{order_id}`                    | Get an order            |
| PATCH  | `/orders/{order_id}/status`             | Update order status     |
| POST   | `/orders/{order_id}/items`              | Add an item to an order |
| PATCH  | `/orders/{order_id}/items/{product_id}` | Update an order item    |
| DELETE | `/orders/{order_id}/items/{product_id}` | Delete an order item    |

## Example

### Create a Product

**Request**

```http
POST /products/
```

```json
{
  "name": "Wireless Mouse",
  "price": 25.99,
  "stock": 50
}
```

**Response**

```json
{
  "id": 1,
  "name": "Wireless Mouse",
  "price": 25.99,
  "stock": 50
}
```

### Create an Order

**Request**

```http
POST /orders/
```

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

The product price is captured as the order item's `unit_price` when the order is created.

## Database Migrations

The project uses Alembic for database schema migrations.

To check the current migration status:

```bash
alembic current
```

To upgrade the database to the latest migration:

```bash
alembic upgrade head
```

To check whether new migration operations are detected:

```bash
alembic check
```

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

Run tests with coverage:

```bash
coverage run -m pytest
coverage report -m
```

Current test result:

```text
61 tests passed
98% overall coverage
```

## Roadmap

Planned improvements include:

* [ ] Product search
* [ ] Low-stock alerts
* [ ] Sales reporting
* [ ] Authentication and authorization
* [ ] PostgreSQL support
* [ ] Docker support
* [ ] Improved project architecture
* [ ] CI/CD integration
* [ ] AI-assisted retail features

## Project Goals

This project is being developed as a practical backend portfolio project to demonstrate:

* Python backend development
* FastAPI development
* REST API design
* SQLAlchemy ORM
* Database modeling
* Business logic implementation
* Inventory management
* Order workflow design
* Database migrations with Alembic
* Automated testing
* Code coverage
* Git and GitHub workflow

## Author

**Mohammad Bornasi**

Python Developer | AI & Automation | Backend Development

* GitHub: [@mohammadbornasi](https://github.com/mohammadbornasi)
* LinkedIn: [Mohammad Bornasi](https://www.linkedin.com/in/mohammadbornasi)

---

If you find this project useful, feel free to explore the repository.
