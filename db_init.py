"""
Database Initialization Script for BoutiqueComplete1
=====================================================
This script:
1. Connects to MongoDB
2. Creates the BoutiqueComplete1 database
3. Inserts sample data (Products, Clients, Orders with embedding and linking)
4. Creates indexes
5. Demonstrates various MongoDB operators and operations
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# --- Configuration ---
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "BoutiqueComplete1"

def get_database():
    """Connect to MongoDB and return the database instance."""
    client = MongoClient(MONGO_URI)
    return client[DATABASE_NAME]

def init_products(db):
    """Initialize Produits collection with 10+ products."""
    products = [
        {"nom": "T-Shirt Blanc", "prix": 19.99, "stock": 100, "categorie": "Vêtements"},
        {"nom": "Jean Slim", "prix": 49.99, "stock": 50, "categorie": "Vêtements"},
        {"nom": "Baskets Running", "prix": 89.99, "stock": 30, "categorie": "Chaussures"},
        {"nom": "Sac à Main Cuir", "prix": 129.99, "stock": 20, "categorie": "Accessoires"},
        {"nom": "Montre Classique", "prix": 199.99, "stock": 15, "categorie": "Accessoires"},
        {"nom": "Chemise Bleue", "prix": 39.99, "stock": 60, "categorie": "Vêtements"},
        {"nom": "Robe d'Été", "prix": 59.99, "stock": 40, "categorie": "Vêtements"},
        {"nom": "Sandales Plage", "prix": 29.99, "stock": 70, "categorie": "Chaussures"},
        {"nom": "Ceinture Cuir", "prix": 34.99, "stock": 45, "categorie": "Accessoires"},
        {"nom": "Lunettes de Soleil", "prix": 79.99, "stock": 25, "categorie": "Accessoires"},
        {"nom": "Pull-over Laine", "prix": 69.99, "stock": 35, "categorie": "Vêtements"},
        {"nom": "Bottes Hiver", "prix": 119.99, "stock": 22, "categorie": "Chaussures"},
    ]
    
    # Drop existing collection and insert fresh data
    db.Produits.drop()
    result = db.Produits.insert_many(products)
    print(f"✅ Inserted {len(result.inserted_ids)} products")
    return result.inserted_ids

def init_clients(db):
    """Initialize Clients collection."""
    clients = [
        {"nom": "Dupont", "prenom": "Marie", "email": "marie.dupont@email.com", "ville": "Paris"},
        {"nom": "Martin", "prenom": "Jean", "email": "jean.martin@email.com", "ville": "Lyon"},
        {"nom": "Bernard", "prenom": "Sophie", "email": "sophie.bernard@email.com", "ville": "Marseille"},
        {"nom": "Petit", "prenom": "Lucas", "email": "lucas.petit@email.com", "ville": "Bordeaux"},
    ]
    
    db.Clients.drop()
    result = db.Clients.insert_many(clients)
    print(f"✅ Inserted {len(result.inserted_ids)} clients")
    return result.inserted_ids

def init_orders_embedding(db, product_ids):
    """Initialize CommandesEmbedding collection (orders with embedded products)."""
    # Fetch some products for embedding
    products = list(db.Produits.find({"_id": {"$in": product_ids[:4]}}))
    
    orders_embedding = [
        {
            "client_nom": "Dupont Marie",
            "date_commande": datetime.now(),
            "statut": "Livrée",
            "produits": [
                {"nom": products[0]["nom"], "prix": products[0]["prix"], "quantite": 2},
                {"nom": products[1]["nom"], "prix": products[1]["prix"], "quantite": 1},
            ],
            "total": products[0]["prix"] * 2 + products[1]["prix"]
        },
        {
            "client_nom": "Martin Jean",
            "date_commande": datetime.now(),
            "statut": "En cours",
            "produits": [
                {"nom": products[2]["nom"], "prix": products[2]["prix"], "quantite": 1},
                {"nom": products[3]["nom"], "prix": products[3]["prix"], "quantite": 1},
            ],
            "total": products[2]["prix"] + products[3]["prix"]
        }
    ]
    
    db.CommandesEmbedding.drop()
    result = db.CommandesEmbedding.insert_many(orders_embedding)
    print(f"✅ Inserted {len(result.inserted_ids)} embedded orders")
    return result.inserted_ids

def init_orders_linking(db, product_ids, client_ids):
    """Initialize CommandesLinking collection (orders with product _id references)."""
    orders_linking = [
        {
            "client_id": client_ids[2],
            "date_commande": datetime.now(),
            "statut": "En préparation",
            "produits": [
                {"produit_id": product_ids[4], "quantite": 1},
                {"produit_id": product_ids[5], "quantite": 2},
            ]
        },
        {
            "client_id": client_ids[3],
            "date_commande": datetime.now(),
            "statut": "Livrée",
            "produits": [
                {"produit_id": product_ids[6], "quantite": 1},
                {"produit_id": product_ids[7], "quantite": 1},
                {"produit_id": product_ids[8], "quantite": 1},
            ]
        }
    ]
    
    db.CommandesLinking.drop()
    result = db.CommandesLinking.insert_many(orders_linking)
    print(f"✅ Inserted {len(result.inserted_ids)} linked orders")
    return result.inserted_ids

def create_indexes(db):
    """Create index on Produits.nom and display existing indexes."""
    # Create index on 'nom' field
    db.Produits.create_index("nom")
    print("✅ Created index on Produits.nom")
    
    # Display all indexes
    print("\n📋 Existing indexes on Produits collection:")
    for index in db.Produits.list_indexes():
        print(f"   - {index['name']}: {index['key']}")

def demonstrate_operators(db):
    """Demonstrate various MongoDB query and update operators."""
    print("\n" + "="*60)
    print("🔍 DEMONSTRATING MONGODB OPERATORS")
    print("="*60)
    
    # --- Query Operators ---
    print("\n--- Query Operators ---")
    
    # $gt (greater than)
    result = list(db.Produits.find({"prix": {"$gt": 50}}, {"nom": 1, "prix": 1}))
    print(f"\n$gt - Products with price > 50: {len(result)} found")
    for p in result[:3]:
        print(f"   {p['nom']}: {p['prix']}€")
    
    # $gte (greater than or equal)
    result = list(db.Produits.find({"stock": {"$gte": 50}}))
    print(f"\n$gte - Products with stock >= 50: {len(result)} found")
    
    # $or
    result = list(db.Produits.find({
        "$or": [
            {"categorie": "Chaussures"},
            {"prix": {"$lt": 30}}
        ]
    }))
    print(f"\n$or - Products in 'Chaussures' OR price < 30: {len(result)} found")
    
    # $in
    result = list(db.Produits.find({
        "categorie": {"$in": ["Vêtements", "Accessoires"]}
    }))
    print(f"\n$in - Products in 'Vêtements' or 'Accessoires': {len(result)} found")
    
    # $exists
    result = list(db.Produits.find({"stock": {"$exists": True}}))
    print(f"\n$exists - Products with 'stock' field: {len(result)} found")
    
    # $regex
    result = list(db.Produits.find({"nom": {"$regex": "^[SC]", "$options": "i"}}))
    print(f"\n$regex - Products starting with 'S' or 'C': {len(result)} found")
    for p in result:
        print(f"   {p['nom']}")
    
    # $where (JavaScript expression)
    result = list(db.Produits.find({
        "$where": "this.prix * this.stock > 1000"
    }))
    print(f"\n$where - Products where prix * stock > 1000: {len(result)} found")
    
    # --- Projection, Sort, Limit, Skip ---
    print("\n--- Projection, Sort, Limit, Skip ---")
    result = list(db.Produits.find(
        {},
        {"nom": 1, "prix": 1, "_id": 0}  # Projection
    ).sort("prix", -1).limit(5).skip(2))
    print(f"\nTop 5 expensive products (skip 2), projection (nom, prix):")
    for p in result:
        print(f"   {p['nom']}: {p['prix']}€")
    
    # --- Update Operators ---
    print("\n--- Update Operators ---")
    
    # $set
    db.Produits.update_one(
        {"nom": "T-Shirt Blanc"},
        {"$set": {"promotion": True, "prix_promo": 14.99}}
    )
    print("\n$set - Added 'promotion' and 'prix_promo' to T-Shirt Blanc")
    
    # $currentDate
    db.Produits.update_one(
        {"nom": "T-Shirt Blanc"},
        {"$currentDate": {"derniere_modification": True}}
    )
    print("$currentDate - Added 'derniere_modification' timestamp")
    
    # $rename
    db.Produits.update_one(
        {"nom": "T-Shirt Blanc"},
        {"$rename": {"prix_promo": "prix_solde"}}
    )
    print("$rename - Renamed 'prix_promo' to 'prix_solde'")
    
    # $unset
    db.Produits.update_one(
        {"nom": "T-Shirt Blanc"},
        {"$unset": {"prix_solde": ""}}
    )
    print("$unset - Removed 'prix_solde' field")
    
    # --- Array Operators ---
    print("\n--- Array Operators ---")
    
    # First, add a 'tags' array to a product
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$set": {"tags": ["mode", "casual"]}}
    )
    
    # $push
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$push": {"tags": "trendy"}}
    )
    print("\n$push - Added 'trendy' to Jean Slim tags")
    
    # $addToSet (won't add duplicate)
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$addToSet": {"tags": "mode"}}  # Already exists, won't duplicate
    )
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$addToSet": {"tags": "premium"}}  # New, will be added
    )
    print("$addToSet - Added 'premium' (unique), 'mode' not duplicated")
    
    # $pull
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$pull": {"tags": "casual"}}
    )
    print("$pull - Removed 'casual' from tags")
    
    # $pop
    db.Produits.update_one(
        {"nom": "Jean Slim"},
        {"$pop": {"tags": 1}}  # Remove last element
    )
    print("$pop - Removed last element from tags")
    
    # Show final state
    product = db.Produits.find_one({"nom": "Jean Slim"})
    print(f"\nFinal tags for Jean Slim: {product.get('tags', [])}")

def demonstrate_aggregation(db):
    """Demonstrate aggregation pipeline - total sales per category."""
    print("\n" + "="*60)
    print("📊 AGGREGATION: Total Sales per Category")
    print("="*60)
    
    # For embedded orders
    pipeline = [
        {"$unwind": "$produits"},
        {"$group": {
            "_id": None,
            "total_ventes": {"$sum": {"$multiply": ["$produits.prix", "$produits.quantite"]}}
        }}
    ]
    
    result = list(db.CommandesEmbedding.aggregate(pipeline))
    if result:
        print(f"\nTotal sales from embedded orders: {result[0]['total_ventes']:.2f}€")
    
    # Product category aggregation
    pipeline = [
        {"$group": {
            "_id": "$categorie",
            "nombre_produits": {"$sum": 1},
            "valeur_stock": {"$sum": {"$multiply": ["$prix", "$stock"]}}
        }},
        {"$sort": {"valeur_stock": -1}}
    ]
    
    result = list(db.Produits.aggregate(pipeline))
    print("\nStock value per category:")
    for cat in result:
        print(f"   {cat['_id']}: {cat['nombre_produits']} products, {cat['valeur_stock']:.2f}€ total value")

def main():
    print("="*60)
    print("🚀 BoutiqueComplete1 - Database Initialization")
    print("="*60)
    
    db = get_database()
    print(f"\n📦 Connected to database: {DATABASE_NAME}")
    
    # Initialize collections
    product_ids = init_products(db)
    client_ids = init_clients(db)
    init_orders_embedding(db, product_ids)
    init_orders_linking(db, product_ids, client_ids)
    
    # Create indexes
    create_indexes(db)
    
    # Demonstrate operators
    demonstrate_operators(db)
    
    # Demonstrate aggregation
    demonstrate_aggregation(db)
    
    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60)

if __name__ == "__main__":
    main()
