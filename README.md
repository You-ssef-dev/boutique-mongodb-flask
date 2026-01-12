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

### 4. Setup MongoDB Authentication (Optional)
If MongoDB is running with authentication enabled, you need to create the database users first.

> **⚠️ Important**: MongoDB must be started **without** the `--auth` flag to run this script for the first time.

```bash
# 1. Stop MongoDB
sudo systemctl stop mongod

# 2. Start MongoDB without authentication (in a separate terminal)
sudo mongod --dbpath /var/lib/mongodb --port 27017

# 3. Run the authentication script
mongosh < db_auth.js

# 4. Stop the temporary MongoDB (Ctrl+C) and restart with authentication
sudo systemctl start mongod
```

**Users created by the script:**
| User | Password | Database | Role |
|------|----------|----------|------|
| `boutiqueAdmin` | `SecurePassword123!` | admin | userAdminAnyDatabase |
| `boutiqueUser` | `BoutiquePass2024!` | BoutiqueComplete1 | readWrite |

**Test the connection:**
```bash
mongosh -u boutiqueUser -p "BoutiquePass2024!" --authenticationDatabase BoutiqueComplete1
```

### 5. Run the Application
```bash
python app.py
```
Open your browser at [http://localhost:5000](http://localhost:5000).

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request.




================================================================================

ALTERNATIVE METHOD (if users already exist):
--------------------------------------------
If you've already created the users before and just want to connect:

mongosh -u boutiqueUser -p "BoutiquePass2024!" --authenticationDatabase BoutiqueComplete1


CREDENTIALS CREATED BY THE SCRIPT:
----------------------------------
Admin User:
  - Username: boutiqueAdmin
  - Password: SecurePassword123!
  - Database: admin

Application User:
  - Username: boutiqueUser  
  - Password: BoutiquePass2024!
  - Database: BoutiqueComplete1
  - Role: readWrite


FOR PYTHON/FLASK CONNECTION:
----------------------------
Use this connection string in your app.py:

mongodb://boutiqueUser:BoutiquePass2024!@localhost:27017/BoutiqueComplete1?authSource=BoutiqueComplete1

================================================================================

chmod +x db_ops.sh
./db_ops.sh
