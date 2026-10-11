# Retail Management API

A RESTful backend API for managing retail operations, built with Python and FastAPI. The project demonstrates API design, database modeling, authentication, inventory management, order workflows, reporting, and automated testing.

## Features

### Product Management
- Create, retrieve, update, and delete products.
- List products with pagination and filtering.
- Track product prices and stock levels.
- Identify products with low stock.

### Customer Management
- Create, retrieve, update, and delete customers.
- List customers with pagination.
- Prevent duplicate customer email addresses.

### Order Management
- Create orders for existing customers.
- Retrieve order details and list orders.
- Add products to orders, update item quantities, and remove items.
- Calculate order totals.
- Preserve item prices when products are added to an order.
- Validate order status transitions.

### Order Status and Inventory
- Manage order status transitions, including confirmation, processing, shipping, delivery, and cancellation.
- Deduct stock when an order is confirmed.
- Restore stock when a confirmed order is cancelled.
- Validate stock availability before confirming orders.

### Inventory Management
- Record stock increases and decreases.
- Store inventory transaction history.
- Track transaction quantities, types, and reasons.
- Prevent stock reductions that exceed available inventory.

### Authentication and Security
- Register and authenticate users.
- Hash passwords before storing them.
- Issue JWT access tokens.
- Retrieve the authenticated user's profile.
- Check account activation status.
- Apply authentication and authorization to protected operations.

### Reporting
- Sales summary and date-based sales reports.
- Reporting endpoints for sales, customers, and inventory.
- Support for analyzing retail operations through aggregated data.

Explore `/docs` after starting the application for the complete, interactive API reference.

## Technology Stack

- **Language:** Python
- **API Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Data Validation:** Pydantic
- **Database Migrations:** Alembic
- **Authentication:** JWT
- **Password Hashing:** pwdlib with Argon2
- **Testing:** Pytest, FastAPI TestClient, HTTPX
- **Version Control:** Git and GitHub

## Project Structure

```text
retail-management-api/
├── alembic/
│   └── versions/
├── routes/
│   ├── auth.py
│   ├── customers.py
│   ├── inventory.py
│   ├── orders.py
│   ├── products.py
│   └── reports.py
├── tests/
│   ├── test_auth.py
│   ├── test_customers.py
│   ├── test_health.py
│   ├── test_inventory.py
│   ├── test_orders.py
│   ├── test_products.py
│   ├── test_reports.py
│   └── test_security.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── security.py
├── alembic.ini
├── requirements.txt
├── .gitignore
└── README.md
```

- `main.py` — application entry point.
- `routes/` — API endpoints grouped by feature.
- `models.py` — SQLAlchemy database models.
- `schemas.py` — Pydantic request and response schemas.
- `database.py` — database configuration and session management.
- `security.py` — authentication and security utilities.
- `alembic/` — database migration configuration and revisions.
- `tests/` — automated API and security tests.

## Getting Started

### Prerequisites

- Python installed and available from the terminal.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/mohammadbornasi/retail-management-api.git
cd retail-management-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the environment

Configure any environment variables required by the application before running it. Keep secrets and local configuration out of version control. Do not commit `.env`, database files, or other sensitive data.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn main:app --reload
```

The API will be available at:

- API root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication

Register a user using `POST /auth/register`, then authenticate through `POST /auth/login`.

Example login request:

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

The response contains a bearer access token:

```json
{
  "access_token": "<access_token>",
  "token_type": "bearer"
}
```

For protected endpoints, include the token in the HTTP `Authorization` header:

```http
Authorization: Bearer <access_token>
```

Use `GET /auth/me` to retrieve the authenticated user's profile.

## API Endpoints

The following table lists the main confirmed endpoints. Open Swagger UI at `/docs` for complete request schemas, query parameters, response models, and error details.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate and obtain a token |
| GET | `/auth/me` | Get the current user's profile |

### Products

| Method | Endpoint | Description |
|---|---|---|
| POST | `/products/` | Create a product |
| GET | `/products/` | List products |
| GET | `/products/low-stock` | List low-stock products |
| GET | `/products/{product_id}` | Retrieve a product |
| PUT | `/products/{product_id}` | Update a product |
| DELETE | `/products/{product_id}` | Delete a product |

### Inventory

| Method | Endpoint | Description |
|---|---|---|
| POST | `/products/{product_id}/inventory` | Record an inventory transaction |
| GET | `/products/{product_id}/inventory` | Retrieve inventory transaction history |

### Customers

| Method | Endpoint | Description |
|---|---|---|
| POST | `/customers/` | Create a customer |
| GET | `/customers/` | List customers |
| GET | `/customers/{customer_id}` | Retrieve a customer |
| PUT | `/customers/{customer_id}` | Update a customer |
| DELETE | `/customers/{customer_id}` | Delete a customer |

### Orders

| Method | Endpoint | Description |
|---|---|---|
| POST | `/orders/` | Create an order |
| GET | `/orders/` | List orders |
| GET | `/orders/{order_id}` | Retrieve an order |
| PATCH | `/orders/{order_id}/status` | Update order status |
| POST | `/orders/{order_id}/items` | Add an item to an order |
| PATCH | `/orders/{order_id}/items/{product_id}` | Update an order item |
| DELETE | `/orders/{order_id}/items/{product_id}` | Remove an order item |

### Reports

The reporting module provides sales summaries and additional reporting endpoints. Consult `/docs` for the exact report paths, filters, pagination options, and response schemas.

## Database Migrations

Alembic manages database schema changes.

Check the current migration revision:

```bash
alembic current
```

Apply migrations:

```bash
alembic upgrade head
```

Check whether model changes require a new migration:

```bash
alembic check
```

## Testing

Run the complete test suite:

```bash
python -m pytest -q
```


The test suite covers authentication, security, products, customers, orders, inventory, reporting, health endpoints, and validation.

**Latest recorded test result:** 260 passed.


## Roadmap

Potential future improvements:

- PostgreSQL support and deployment configuration.
- Docker-based development and deployment.
- Continuous integration and automated quality checks.
- More advanced reporting and analytics.
- Additional API documentation and integration examples.
- Production deployment and monitoring improvements.

## Project Goals

This project serves as a practical backend development portfolio, demonstrating:

- RESTful API development with FastAPI.
- Relational data modeling and SQLAlchemy ORM.
- Request validation and structured API responses.
- Authentication, password hashing, and access control.
- Transactional business logic for orders and inventory.
- Database migrations with Alembic.
- Automated testing and code coverage.
- Git and GitHub development workflows.

## Author

**Mohammad Bornasi**

Python Developer | Backend Development | AI & Automation

- GitHub: [@mohammadbornasi](https://github.com/mohammadbornasi)
- LinkedIn: [Mohammad Bornasi](https://www.linkedin.com/in/mohammadbornasi)

---

If you find this project useful, feel free to explore the repository.
