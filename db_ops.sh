#!/bin/bash
# MongoDB Export/Import Script for BoutiqueComplete1
# ===================================================

echo "========================================"
echo "📦 MongoDB Export/Import Operations"
echo "========================================"

# Configuration
DB_NAME="BoutiqueComplete1"
EXPORT_DIR="./exports"

# Create export directory if not exists
mkdir -p $EXPORT_DIR

echo ""
echo "--- EXPORT OPERATIONS ---"
echo ""

# Export Produits collection to JSON
echo "📤 Exporting Produits to JSON..."
mongoexport --db=$DB_NAME --collection=Produits --out=$EXPORT_DIR/produits.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/produits.json"

# Export Clients collection
echo "📤 Exporting Clients to JSON..."
mongoexport --db=$DB_NAME --collection=Clients --out=$EXPORT_DIR/clients.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/clients.json"

# Export Orders (Embedding)
echo "📤 Exporting CommandesEmbedding to JSON..."
mongoexport --db=$DB_NAME --collection=CommandesEmbedding --out=$EXPORT_DIR/commandes_embedding.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/commandes_embedding.json"

# Export Orders (Linking)
echo "📤 Exporting CommandesLinking to JSON..."
mongoexport --db=$DB_NAME --collection=CommandesLinking --out=$EXPORT_DIR/commandes_linking.json --jsonArray
echo "   ✅ Exported to $EXPORT_DIR/commandes_linking.json"

echo ""
echo "--- IMPORT OPERATIONS ---"
echo ""

# Re-import Produits (with drop to avoid duplicates in demo)
echo "📥 Re-importing Produits from JSON..."
mongoimport --db=$DB_NAME --collection=Produits --file=$EXPORT_DIR/produits.json --jsonArray --drop
echo "   ✅ Imported from $EXPORT_DIR/produits.json"

echo ""
echo "========================================"
echo "✅ Export/Import operations complete!"
echo "========================================"
echo ""
echo "📁 Exported files location: $EXPORT_DIR/"
ls -la $EXPORT_DIR/
