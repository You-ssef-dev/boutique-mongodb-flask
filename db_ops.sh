#!/bin/bash
# MongoDB Export/Import Script for BoutiqueComplete1
# ===================================================

echo "========================================"
echo "📦 MongoDB Export/Import Operations"
echo "========================================"

# Configuration
DB_NAME="BoutiqueComplete1"
EXPORT_DIR="./exports"
DATE=$(date +%F)

# Authentication Details
AUTH_URI="mongodb://boutiqueUser:BoutiquePass2024!@localhost:27017/BoutiqueComplete1?authSource=BoutiqueComplete1"

# Create export directory if not exists
mkdir -p $EXPORT_DIR

echo ""
echo "Choose an option:"
echo "1) EXPORT database (backup to JSON)"
echo "2) IMPORT database (restore from JSON)"
echo "0) Exit"
echo "----------------------------------------"
read -p "👉 Enter your choice: " choice


case $choice in

# ================================
# 1) EXPORT SECTION
# ================================
1)
echo ""
echo "--- EXPORT OPERATIONS ---"
echo ""

echo "📤 Exporting Produits to JSON..."
mongoexport --uri="$AUTH_URI" --collection=Produits --out=$EXPORT_DIR/produits_$DATE.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/produits_$DATE.json"

echo "📤 Exporting Clients to JSON..."
mongoexport --uri="$AUTH_URI" --collection=Clients --out=$EXPORT_DIR/clients_$DATE.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/clients_$DATE.json"

echo "📤 Exporting CommandesEmbedding to JSON..."
mongoexport --uri="$AUTH_URI" --collection=CommandesEmbedding --out=$EXPORT_DIR/commandes_embedding_$DATE.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/commandes_embedding_$DATE.json"

echo "📤 Exporting CommandesLinking to JSON..."
mongoexport --uri="$AUTH_URI" --collection=CommandesLinking --out=$EXPORT_DIR/commandes_linking_$DATE.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/commandes_linking_$DATE.json"

echo ""
echo "========================================"
echo "✅ EXPORT completed successfully!"
echo "========================================"
;;

# ================================
# 2) IMPORT SECTION
# ================================
2)
echo ""
echo "--- IMPORT OPERATIONS ---"
echo "⚠️ Warning: existing collections will be DROPPED before restore"
echo ""

mongoimport --uri="$AUTH_URI" --collection=Produits --file=$EXPORT_DIR/produits_$DATE.json --jsonArray --drop
mongoimport --uri="$AUTH_URI" --collection=Clients --file=$EXPORT_DIR/clients_$DATE.json --jsonArray --drop
mongoimport --uri="$AUTH_URI" --collection=CommandesEmbedding --file=$EXPORT_DIR/commandes_embedding_$DATE.json --jsonArray --drop
mongoimport --uri="$AUTH_URI" --collection=CommandesLinking --file=$EXPORT_DIR/commandes_linking_$DATE.json --jsonArray --drop

echo ""
echo "========================================"
echo "✅ IMPORT completed from backup date: $DATE"
echo "========================================"
;;

0)
echo "👋 Exit"
exit 0
;;

*)
echo "❌ Invalid choice"
;;
esac

echo ""
echo "📁 Exported files location: $EXPORT_DIR/"
ls -la $EXPORT_DIR/
