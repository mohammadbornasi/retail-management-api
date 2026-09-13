# Retail Management API

A practical REST API for managing products and inventory, built with Python and FastAPI.

## 🚀 About the Project

Retail Management API is a backend application designed as a foundation for managing products in a retail environment.

The project demonstrates how to build a RESTful API using Python, FastAPI, SQLAlchemy, and SQLite.

The goal is to gradually expand this project into a complete retail management system with products, customers, sales, inventory tracking, and reporting.

## ✨ Current Features

- Create products
- List all products
- Retrieve a product by ID
- Update products
- Delete products
- SQLite database integration
- Automatic API documentation with Swagger UI
- RESTful API structure
- Git and GitHub version control

## 🛠️ Technologies

- Python 3.14
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn
- Git & GitHub

## 📁 Project Structure

```text
retail-management-api/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
│
├── routes/
│   └── products.py
│
├── .gitignore
└── README.md
```

> The SQLite database and virtual environment are excluded from GitHub using `.gitignore`.

## ⚙️ Installation

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
pip install fastapi uvicorn sqlalchemy
```

## ▶️ Running the API

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## 📚 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

## 🔌 API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products/` | Create a product |
| GET | `/products/` | Get all products |
| GET | `/products/{id}` | Get a product |
| PUT | `/products/{id}` | Update a product |
| DELETE | `/products/{id}` | Delete a product |

## 🧪 Example

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

## 🗺️ Roadmap

Future versions will include:

- [ ] Customer management
- [ ] Sales management
- [ ] Inventory tracking
- [ ] Sales reports
- [ ] Product search
- [ ] Low-stock alerts
- [ ] Data validation improvements
- [ ] Authentication and authorization
- [ ] PostgreSQL support
- [ ] Docker support
- [ ] AI-powered features

## 🎯 Project Goals

This project is being developed as a practical software engineering project to demonstrate:

- Python backend development
- REST API design
- Database integration
- Software architecture
- API documentation
- Version control with Git
- Continuous project improvement

## 👨‍💻 Author

**Mohammad Bornasi**

Python Developer | AI & Automation | Web Development

- GitHub: [@mohammadbornasi](https://github.com/mohammadbornasi)
- LinkedIn: [Mohammad Bornasi](https://www.linkedin.com/in/mohammadbornasi)

---

⭐ If you find this project useful, feel free to explore the repository.
