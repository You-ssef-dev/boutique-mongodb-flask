# 🛍️ BoutiqueComplete1 - Full Stack Mongo Shop

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?style=for-the-badge&logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

A complete **E-commerce Management System** built to demonstrate advanced **MongoDB** patterns and **Flask** development. This project implements a full CRUD application with specific focus on NoSQL data modeling concepts (Embedding vs Linking) and complex aggregation pipelines.

---

## ✨ Features

### 📦 Product Management (CRUD)
- **Create, Read, Update, Delete** products.
- **Advanced Filtering**: Filter by category, price range, and stock levels.
- **Search**: Real-time search using MongoDB `$regex`.
- **Tags**: Manage product tags using array operators (`$push`, `$pull`, `$addToSet`).

### 🛒 Order Management (NoSQL Patterns)
This project demonstrates two different ways to model data in MongoDB:
1.  **Embedding Pattern**: Orders store the full product details snapshot inside the order document. Optimal for read performance and historical records.
2.  **Linking Pattern**: Orders store only product References (`_id`). Data is joined at runtime using `$lookup`. Optimal for data consistency.

### 📊 Analytics & Aggregation
- **Sales Statistics**: Calculated using `$unwind` and `$group` stages.
- **Stock Analysis**: Total inventory value calculated per category.
- **Top Products**: Best sellers identified using sorting and limits.

### 🛠️ Advanced MongoDB Operators
The application includes a dedicated interface to test:
- **Query Operators**: `$gt`, `$gte`, `$in`, `$or`, `$exists`, `$where`.
- **Update Operators**: `$set`, `$unset`, `$rename`, `$currentDate`.
- **Array Operators**: `$push`, `$pop`, `$pull`, `$addToSet`.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher
- MongoDB running locally on port 27017

### 2. Clone and Install
```bash
git clone https://github.com/You-ssef-dev/boutique-mongodb-flask.git
cd boutique-mongodb-flask

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database
Run the initialization script to seed the database with sample products, clients, and orders.
```bash
python db_init.py
```

### 4. Run the Application
```bash
python app.py
```
Open your browser at [http://localhost:5000](http://localhost:5000).

---

## 📂 Project Structure

- `app.py`: Main Flask application containing all API routes and controller logic.
- `db_init.py`: Python script to reset the database and populate it with initial data.
- `db_auth.js`: MongoDB shell script to create users and set up authentication.
- `db_ops.sh`: Bash script to demonstrating `mongoexport` and `mongoimport` capabilities.
- `static/`: Contains `style.css` (Modern Dashboard UI) and `main.js` (Frontend logic).
- `templates/`: HTML Jinja2 templates for the user interface.

## 🔒 Security & Operations
- **Authentication**: Includes `db_auth.js` to create a `boutiqueUser` with `readWrite` roles.
- **Backup**: Includes scripts to export the `Produits` collection to JSON and re-import it.

## 🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request.
