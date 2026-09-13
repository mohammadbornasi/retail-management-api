\# Retail Management API



A practical REST API for managing products and inventory, built with Python and FastAPI.



\## 🚀 About the Project



Retail Management API is a backend application designed to provide a foundation for managing products in a retail environment.



The project demonstrates the implementation of a RESTful API using Python, FastAPI, SQLAlchemy, and SQLite.



The goal is to gradually expand this project into a complete retail management system with products, customers, sales, inventory tracking, and reporting.



\## ✨ Current Features



\- Create products

\- List all products

\- Retrieve a product by ID

\- Update products

\- Delete products

\- SQLite database integration

\- Automatic API documentation with Swagger UI

\- RESTful API structure

\- Git and GitHub version control



\## 🛠️ Technologies



\- Python 3.14

\- FastAPI

\- SQLAlchemy

\- SQLite

\- Pydantic

\- Uvicorn

\- Git \& GitHub



\## 📁 Project Structure



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

├── README.md

└── retail.db



The SQLite database and virtual environment are kept out of GitHub through .gitignore.



⚙️ Installation

1\. Clone the repository

git clone https://github.com/mohammadbornasi/retail-management-api.git

2\. Navigate to the project

cd retail-management-api

3\. Create a virtual environment

python -m venv .venv

4\. Activate the virtual environment

Windows PowerShell

.\\.venv\\Scripts\\Activate.ps1

5\. Install dependencies

pip install fastapi uvicorn sqlalchemy

▶️ Running the API



Start the development server:



uvicorn main:app --reload



The API will be available at:



http://127.0.0.1:8000

📚 API Documentation



FastAPI automatically provides interactive API documentation.



Swagger UI:



http://127.0.0.1:8000/docs



Alternative documentation:



http://127.0.0.1:8000/redoc

🔌 API Endpoints

Products

Method	Endpoint	Description

POST	/products/	Create a product

GET	/products/	Get all products

GET	/products/{id}	Get a product

PUT	/products/{id}	Update a product

DELETE	/products/{id}	Delete a product

🧪 Example

Create a Product

POST /products/



Request:



{

&#x20; "name": "Wireless Mouse",

&#x20; "price": 25.99,

&#x20; "stock": 50

}



Response:



{

&#x20; "id": 1,

&#x20; "name": "Wireless Mouse",

&#x20; "price": 25.99,

&#x20; "stock": 50

}

🗺️ Roadmap



Future versions will include:



&#x20;Customer management

&#x20;Sales management

&#x20;Inventory tracking

&#x20;Sales reports

&#x20;Product search

&#x20;Low-stock alerts

&#x20;Data validation improvements

&#x20;Authentication and authorization

&#x20;PostgreSQL support

&#x20;Docker support

&#x20;AI-powered features

🎯 Project Goals



This project is being developed as a practical software engineering project to demonstrate:



Python backend development

REST API design

Database integration

Software architecture

API documentation

Version control with Git

Continuous project improvement

👨‍💻 Author



Mohammad Bornasi



Python Developer | AI \& Automation | Web Development



GitHub: @mohammadbornasi

LinkedIn: Mohammad Bornasi



⭐ If you find this project useful, feel free to explore the repository.

