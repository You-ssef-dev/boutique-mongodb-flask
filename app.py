"""
BoutiqueComplete1 - Flask Backend Application
==============================================
A complete REST API for an online shop management system.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from pymongo import MongoClient
from bson import ObjectId, json_util
from datetime import datetime
import json

# --- Flask App Configuration ---
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- MongoDB Configuration ---
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "BoutiqueComplete1"

def get_db():
    """Get database connection."""
    client = MongoClient(MONGO_URI)
    return client[DATABASE_NAME]

def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc

# ============================================================
# PAGE ROUTES (HTML Templates)
# ============================================================

@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('index.html')

@app.route('/products')
def products_page():
    """Products management page."""
    return render_template('products.html')

@app.route('/orders')
def orders_page():
    """Orders management page."""
    return render_template('orders.html')

@app.route('/aggregation')
def aggregation_page():
    """Aggregation results page."""
    return render_template('aggregation.html')

@app.route('/search')
def search_page():
    """Search and filter tests page."""
    return render_template('search.html')

@app.route('/documentation')
def documentation():
    """Project documentation page."""
    return send_from_directory('docs', 'index.html')

@app.route('/docs/<path:filename>')
def serve_docs(filename):
    """Serve documentation static files."""
    return send_from_directory('docs', filename)

# ============================================================
# API ROUTES - PRODUCTS (CRUD)
# ============================================================

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Get all products with optional filters, sort, limit, skip.
    Query params: 
      - categorie: filter by category
      - min_prix: minimum price ($gte)
      - max_prix: maximum price ($lte)
      - search: regex search on nom
      - sort: field to sort by (prefix with - for descending)
      - limit: number of results
      - skip: number to skip (pagination)
    """
    db = get_db()
    
    # Build query filter
    query = {}
    
    # Category filter ($in operator if multiple)
    categorie = request.args.get('categorie')
    if categorie:
        categories = categorie.split(',')
        if len(categories) > 1:
            query['categorie'] = {'$in': categories}
        else:
            query['categorie'] = categorie
    
    # Price filters ($gte, $gt, $lte)
    min_prix = request.args.get('min_prix', type=float)
    max_prix = request.args.get('max_prix', type=float)
    if min_prix is not None or max_prix is not None:
        query['prix'] = {}
        if min_prix is not None:
            query['prix']['$gte'] = min_prix
        if max_prix is not None:
            query['prix']['$lte'] = max_prix
    
    # Stock filter
    min_stock = request.args.get('min_stock', type=int)
    if min_stock is not None:
        query['stock'] = {'$gt': min_stock}
    
    # Regex search on nom
    search = request.args.get('search')
    if search:
        query['nom'] = {'$regex': search, '$options': 'i'}
    
    # Check if field exists
    has_field = request.args.get('has_field')
    if has_field:
        query[has_field] = {'$exists': True}
    
    # Build cursor with sort, limit, skip
    cursor = db.Produits.find(query)
    
    # Sorting
    sort_field = request.args.get('sort', 'nom')
    sort_order = 1
    if sort_field.startswith('-'):
        sort_field = sort_field[1:]
        sort_order = -1
    cursor = cursor.sort(sort_field, sort_order)
    
    # Pagination
    limit = request.args.get('limit', type=int)
    skip = request.args.get('skip', type=int, default=0)
    
    if skip:
        cursor = cursor.skip(skip)
    if limit:
        cursor = cursor.limit(limit)
    
    products = list(cursor)
    
    # Get total count for pagination
    total = db.Produits.count_documents(query)
    
    return jsonify({
        'success': True,
        'data': serialize_doc(products),
        'total': total,
        'skip': skip,
        'limit': limit
    })

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID."""
    db = get_db()
    try:
        product = db.Produits.find_one({'_id': ObjectId(product_id)})
        if product:
            return jsonify({'success': True, 'data': serialize_doc(product)})
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product."""
    db = get_db()
    data = request.get_json()
    
    # Validate required fields
    required = ['nom', 'prix', 'stock', 'categorie']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
    
    # Insert product
    product = {
        'nom': data['nom'],
        'prix': float(data['prix']),
        'stock': int(data['stock']),
        'categorie': data['categorie']
    }
    
    # Add optional fields
    if 'tags' in data:
        product['tags'] = data['tags']
    
    result = db.Produits.insert_one(product)
    product['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'data': product, 'message': 'Product created successfully'}), 201

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update a product. Supports various update operators.
    Body can contain:
      - Direct fields to update (uses $set)
      - $set, $unset, $rename, $currentDate operators
      - Array operators: $push, $addToSet, $pull, $pop
    """
    db = get_db()
    data = request.get_json()
    
    try:
        object_id = ObjectId(product_id)
    except:
        return jsonify({'success': False, 'error': 'Invalid product ID'}), 400
    
    # Check if product exists
    existing = db.Produits.find_one({'_id': object_id})
    if not existing:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    
    # Build update document
    update = {}
    
    # Handle explicit operators
    operators = ['$set', '$unset', '$rename', '$currentDate', '$push', '$addToSet', '$pull', '$pop']
    for op in operators:
        if op in data:
            update[op] = data[op]
    
    # If no operators specified, use $set for all fields
    if not update:
        # Remove _id if present
        data.pop('_id', None)
        update['$set'] = data
    
    # Always add modification timestamp
    if '$currentDate' not in update:
        update['$currentDate'] = {}
    update['$currentDate']['derniere_modification'] = True
    
    result = db.Produits.update_one({'_id': object_id}, update)
    
    if result.modified_count > 0:
        updated = db.Produits.find_one({'_id': object_id})
        return jsonify({
            'success': True, 
            'data': serialize_doc(updated),
            'message': 'Product updated successfully'
        })
    
    return jsonify({'success': True, 'message': 'No changes made'})

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product."""
    db = get_db()
    try:
        result = db.Produits.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# API ROUTES - PRODUCTS ARRAY OPERATIONS
# ============================================================

@app.route('/api/products/<product_id>/tags', methods=['POST'])
def add_tag(product_id):
    """Add tag to product using $push or $addToSet."""
    db = get_db()
    data = request.get_json()
    tag = data.get('tag')
    unique_only = data.get('unique', True)
    
    if not tag:
        return jsonify({'success': False, 'error': 'Tag is required'}), 400
    
    try:
        operator = '$addToSet' if unique_only else '$push'
        result = db.Produits.update_one(
            {'_id': ObjectId(product_id)},
            {operator: {'tags': tag}}
        )
        
        updated = db.Produits.find_one({'_id': ObjectId(product_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': f'Tag added using {operator}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/products/<product_id>/tags', methods=['DELETE'])
def remove_tag(product_id):
    """Remove tag from product using $pull."""
    db = get_db()
    data = request.get_json()
    tag = data.get('tag')
    
    if not tag:
        return jsonify({'success': False, 'error': 'Tag is required'}), 400
    
    try:
        result = db.Produits.update_one(
            {'_id': ObjectId(product_id)},
            {'$pull': {'tags': tag}}
        )
        
        updated = db.Produits.find_one({'_id': ObjectId(product_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Tag removed using $pull'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/products/<product_id>/tags/pop', methods=['POST'])
def pop_tag(product_id):
    """Remove first or last tag using $pop."""
    db = get_db()
    data = request.get_json() or {}
    position = data.get('position', 'last')  # 'first' or 'last'
    
    try:
        pop_value = 1 if position == 'last' else -1
        result = db.Produits.update_one(
            {'_id': ObjectId(product_id)},
            {'$pop': {'tags': pop_value}}
        )
        
        updated = db.Produits.find_one({'_id': ObjectId(product_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': f'Removed {position} tag using $pop'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# API ROUTES - ORDERS (EMBEDDING)
# ============================================================

@app.route('/api/orders/embedding', methods=['GET'])
def get_orders_embedding():
    """Get all orders with embedded products."""
    db = get_db()
    orders = list(db.CommandesEmbedding.find())
    return jsonify({'success': True, 'data': serialize_doc(orders)})

@app.route('/api/orders/embedding', methods=['POST'])
def create_order_embedding():
    """Create order with embedded products."""
    db = get_db()
    data = request.get_json()
    
    # Validate
    if 'client_nom' not in data or 'produits' not in data:
        return jsonify({'success': False, 'error': 'client_nom and produits required'}), 400
    
    # Calculate total
    total = sum(p.get('prix', 0) * p.get('quantite', 1) for p in data['produits'])
    
    order = {
        'client_nom': data['client_nom'],
        'date_commande': datetime.now(),
        'statut': data.get('statut', 'En cours'),
        'produits': data['produits'],
        'total': total
    }
    
    result = db.CommandesEmbedding.insert_one(order)
    order['_id'] = str(result.inserted_id)
    
    return jsonify({
        'success': True,
        'data': serialize_doc(order),
        'message': 'Embedded order created'
    }), 201

@app.route('/api/orders/embedding/<order_id>/products', methods=['POST'])
def add_product_to_embedding(order_id):
    """Add product to embedded order using $push."""
    db = get_db()
    data = request.get_json()
    
    if 'nom' not in data or 'prix' not in data:
        return jsonify({'success': False, 'error': 'nom and prix required'}), 400
    
    product = {
        'nom': data['nom'],
        'prix': float(data['prix']),
        'quantite': int(data.get('quantite', 1))
    }
    
    try:
        # Add product and update total
        db.CommandesEmbedding.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$push': {'produits': product},
                '$inc': {'total': product['prix'] * product['quantite']}
            }
        )
        
        updated = db.CommandesEmbedding.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Product added to order'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/orders/embedding/<order_id>/products', methods=['DELETE'])
def remove_product_from_embedding(order_id):
    """Remove product from embedded order using $pull."""
    db = get_db()
    data = request.get_json()
    product_nom = data.get('nom')
    
    if not product_nom:
        return jsonify({'success': False, 'error': 'Product nom required'}), 400
    
    try:
        # Get order to calculate total reduction
        order = db.CommandesEmbedding.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Find product to remove
        product_to_remove = next((p for p in order['produits'] if p['nom'] == product_nom), None)
        if not product_to_remove:
            return jsonify({'success': False, 'error': 'Product not in order'}), 404
        
        reduction = product_to_remove['prix'] * product_to_remove['quantite']
        
        db.CommandesEmbedding.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$pull': {'produits': {'nom': product_nom}},
                '$inc': {'total': -reduction}
            }
        )
        
        updated = db.CommandesEmbedding.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Product removed from order'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orders/embedding/<order_id>', methods=['DELETE'])
def delete_order_embedding(order_id):
    """Delete an embedded order."""
    db = get_db()
    
    try:
        result = db.CommandesEmbedding.delete_one({'_id': ObjectId(order_id)})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Embedded order deleted'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orders/embedding/<order_id>', methods=['PUT'])
def update_order_embedding(order_id):
    """Update an embedded order (status, client_nom)."""
    db = get_db()
    data = request.get_json()
    
    try:
        update_fields = {}
        
        if 'statut' in data:
            update_fields['statut'] = data['statut']
        if 'client_nom' in data:
            update_fields['client_nom'] = data['client_nom']
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        result = db.CommandesEmbedding.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': update_fields}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        updated = db.CommandesEmbedding.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Embedded order updated'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# API ROUTES - ORDERS (LINKING)
# ============================================================

@app.route('/api/orders/linking', methods=['GET'])
def get_orders_linking():
    """Get all orders with linked products (resolved)."""
    db = get_db()
    
    # Use $lookup to join products
    pipeline = [
        {
            '$lookup': {
                'from': 'Produits',
                'localField': 'produits.produit_id',
                'foreignField': '_id',
                'as': 'produits_details'
            }
        },
        {
            '$lookup': {
                'from': 'Clients',
                'localField': 'client_id',
                'foreignField': '_id',
                'as': 'client_details'
            }
        }
    ]
    
    orders = list(db.CommandesLinking.aggregate(pipeline))
    return jsonify({'success': True, 'data': serialize_doc(orders)})

@app.route('/api/orders/linking', methods=['POST'])
def create_order_linking():
    """Create order with product references (linking)."""
    db = get_db()
    data = request.get_json()
    
    if 'client_id' not in data or 'produits' not in data:
        return jsonify({'success': False, 'error': 'client_id and produits required'}), 400
    
    # Convert product IDs to ObjectId
    produits = []
    for p in data['produits']:
        produits.append({
            'produit_id': ObjectId(p['produit_id']),
            'quantite': int(p.get('quantite', 1))
        })
    
    order = {
        'client_id': ObjectId(data['client_id']),
        'date_commande': datetime.now(),
        'statut': data.get('statut', 'En cours'),
        'produits': produits
    }
    
    result = db.CommandesLinking.insert_one(order)
    order['_id'] = str(result.inserted_id)
    
    return jsonify({
        'success': True,
        'data': serialize_doc(order),
        'message': 'Linked order created'
    }), 201

@app.route('/api/orders/linking/<order_id>/products', methods=['POST'])
def add_product_to_linking(order_id):
    """Add product reference to linked order."""
    db = get_db()
    data = request.get_json()
    
    if 'produit_id' not in data:
        return jsonify({'success': False, 'error': 'produit_id required'}), 400
    
    try:
        db.CommandesLinking.update_one(
            {'_id': ObjectId(order_id)},
            {'$push': {'produits': {
                'produit_id': ObjectId(data['produit_id']),
                'quantite': int(data.get('quantite', 1))
            }}}
        )
        
        updated = db.CommandesLinking.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Product added to linked order'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/orders/linking/<order_id>/products/<product_id>', methods=['DELETE'])
def remove_product_from_linking(order_id, product_id):
    """Remove product reference from linked order."""
    db = get_db()
    
    try:
        db.CommandesLinking.update_one(
            {'_id': ObjectId(order_id)},
            {'$pull': {'produits': {'produit_id': ObjectId(product_id)}}}
        )
        
        updated = db.CommandesLinking.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Product removed from linked order'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orders/linking/<order_id>', methods=['DELETE'])
def delete_order_linking(order_id):
    """Delete a linked order."""
    db = get_db()
    
    try:
        result = db.CommandesLinking.delete_one({'_id': ObjectId(order_id)})
        
        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Linked order deleted'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orders/linking/<order_id>', methods=['PUT'])
def update_order_linking(order_id):
    """Update a linked order (status)."""
    db = get_db()
    data = request.get_json()
    
    try:
        update_fields = {}
        
        if 'statut' in data:
            update_fields['statut'] = data['statut']
        
        if not update_fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        result = db.CommandesLinking.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': update_fields}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        updated = db.CommandesLinking.find_one({'_id': ObjectId(order_id)})
        return jsonify({
            'success': True,
            'data': serialize_doc(updated),
            'message': 'Linked order updated'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# API ROUTES - CLIENTS
# ============================================================

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients."""
    db = get_db()
    clients = list(db.Clients.find())
    return jsonify({'success': True, 'data': serialize_doc(clients)})

# ============================================================
# API ROUTES - AGGREGATION
# ============================================================

@app.route('/api/stats/sales-by-category', methods=['GET'])
def sales_by_category():
    """Calculate total sales per category using aggregation."""
    db = get_db()
    
    # Aggregation on embedded orders
    pipeline = [
        {'$unwind': '$produits'},
        {'$lookup': {
            'from': 'Produits',
            'localField': 'produits.nom',
            'foreignField': 'nom',
            'as': 'details_produit'
        }},
        {'$unwind': '$details_produit'},
        {'$group': {
            '_id': '$details_produit.categorie',
            'total_ventes': {'$sum': {'$multiply': ['$produits.prix', '$produits.quantite']}},
            'nombre_articles': {'$sum': '$produits.quantite'}
        }}
    ]
    
    embedded_result = list(db.CommandesEmbedding.aggregate(pipeline))
    
    return jsonify({
        'success': True,
        'data': {
            'embedded_orders': serialize_doc(embedded_result),
        }
    })

@app.route('/api/stats/stock-by-category', methods=['GET'])
def stock_by_category():
    """Get stock value per category."""
    db = get_db()
    
    pipeline = [
        {'$group': {
            '_id': '$categorie',
            'nombre_produits': {'$sum': 1},
            'stock_total': {'$sum': '$stock'},
            'valeur_stock': {'$sum': {'$multiply': ['$prix', '$stock']}},
            'prix_moyen': {'$avg': '$prix'}
        }},
        {'$sort': {'valeur_stock': -1}}
    ]
    
    result = list(db.Produits.aggregate(pipeline))
    
    return jsonify({'success': True, 'data': serialize_doc(result)})

@app.route('/api/stats/top-products', methods=['GET'])
def top_products():
    """Get top selling products from embedded orders."""
    db = get_db()
    
    pipeline = [
        {'$unwind': '$produits'},
        {'$group': {
            '_id': '$produits.nom',
            'quantite_vendue': {'$sum': '$produits.quantite'},
            'revenue': {'$sum': {'$multiply': ['$produits.prix', '$produits.quantite']}}
        }},
        {'$sort': {'quantite_vendue': -1}},
        {'$limit': 10}
    ]
    
    result = list(db.CommandesEmbedding.aggregate(pipeline))
    
    return jsonify({'success': True, 'data': serialize_doc(result)})

# ============================================================
# API ROUTES - INDEXES
# ============================================================

@app.route('/api/indexes', methods=['GET'])
def get_indexes():
    """Get all indexes on Produits collection."""
    db = get_db()
    indexes = []
    for index in db.Produits.list_indexes():
        indexes.append({
            'name': index['name'],
            'key': dict(index['key']),
            'unique': index.get('unique', False)
        })
    return jsonify({'success': True, 'data': indexes})

@app.route('/api/indexes', methods=['POST'])
def create_index():
    """Create an index on Produits collection."""
    db = get_db()
    data = request.get_json()
    field = data.get('field')
    
    if not field:
        return jsonify({'success': False, 'error': 'Field name required'}), 400
    
    try:
        index_name = db.Produits.create_index(field)
        return jsonify({
            'success': True,
            'message': f'Index created: {index_name}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================
# API ROUTES - ADVANCED QUERY OPERATORS DEMO
# ============================================================

@app.route('/api/demo/operators', methods=['POST'])
def demo_operators():
    """
    Demonstrate various MongoDB query operators.
    Body: { "operator": "$gt|$gte|$or|$in|$exists|$regex|$where", "params": {...} }
    """
    db = get_db()
    data = request.get_json()
    operator = data.get('operator')
    params = data.get('params', {})
    
    query = {}
    
    if operator == '$gt':
        field = params.get('field', 'prix')
        value = params.get('value', 50)
        query[field] = {'$gt': value}
        
    elif operator == '$gte':
        field = params.get('field', 'stock')
        value = params.get('value', 50)
        query[field] = {'$gte': value}
        
    elif operator == '$or':
        conditions = params.get('conditions', [
            {'categorie': 'Chaussures'},
            {'prix': {'$lt': 30}}
        ])
        query['$or'] = conditions
        
    elif operator == '$in':
        field = params.get('field', 'categorie')
        values = params.get('values', ['Vêtements', 'Accessoires'])
        query[field] = {'$in': values}
        
    elif operator == '$exists':
        field = params.get('field', 'tags')
        exists = params.get('exists', True)
        query[field] = {'$exists': exists}
        
    elif operator == '$regex':
        field = params.get('field', 'nom')
        pattern = params.get('pattern', '^[SC]')
        options = params.get('options', 'i')
        query[field] = {'$regex': pattern, '$options': options}
        
    elif operator == '$where':
        expression = params.get('expression', 'this.prix * this.stock > 1000')
        query['$where'] = expression

    # --- Update Operators ---
    elif operator in ['$set', '$unset', '$rename', '$currentDate', '$push', '$addToSet', '$pop', '$pull']:
        # For demo purposes, we'll update ALL documents that match a basic filter (or all if none)
        # But to be safe and clear, let's target specific items or generic filter if provided
        # For this demo, let's update everything so the user sees the effect immediately on the list
        filter_query = {} 
        update_query = {}

        if operator == '$set':
            field = params.get('field', 'prix')
            value = params.get('value', 100)
            update_query['$set'] = {field: value}

        elif operator == '$unset':
            field = params.get('field', 'details')
            update_query['$unset'] = {field: ""}

        elif operator == '$rename':
            field = params.get('field', 'oldName')
            new_name = params.get('newName', 'newName')
            update_query['$rename'] = {field: new_name}

        elif operator == '$currentDate':
            field = params.get('field', 'lastModified')
            type_val = params.get('type', 'date') # or timestamp
            update_query['$currentDate'] = {field: {'$type': type_val}}

        # --- Array Operators ---
        elif operator == '$push':
            field = params.get('field', 'tags')
            value = params.get('value', 'nouveau')
            update_query['$push'] = {field: value}

        elif operator == '$addToSet':
            field = params.get('field', 'tags')
            value = params.get('value', 'unique')
            update_query['$addToSet'] = {field: value}

        elif operator == '$pop':
            field = params.get('field', 'tags')
            # 1 for last, -1 for first. Frontend should send number or we parse it
            value = int(params.get('value', 1)) 
            update_query['$pop'] = {field: value}

        elif operator == '$pull':
            field = params.get('field', 'tags')
            value = params.get('value', 'outdated')
            update_query['$pull'] = {field: value}

        # Execute Update
        result = db.Produits.update_many(filter_query, update_query)
        
        # return all docs to see changes
        results = list(db.Produits.find({}))
        
        return jsonify({
            'success': True,
            'operator': operator,
            'query': json.loads(json_util.dumps(update_query)),
            'count': len(results),
            'modified_count': result.modified_count,
            'data': serialize_doc(results)
        })

    else:
        return jsonify({'success': False, 'error': f'Unknown operator: {operator}'}), 400
    
    # Apply projection if specified
    projection = params.get('projection')
    
    results = list(db.Produits.find(query, projection))
    
    return jsonify({
        # Indique que la requête a été exécutée avec succès
        # Le frontend peut vérifier ce champ pour savoir si tout s’est bien passé
        'success': True,

        # Nom de l’opérateur MongoDB utilisé pour construire la requête
        # Exemple : "$gt", "$or", "$expr"
        'operator': operator,

        # Requête MongoDB réellement utilisée
        # json_util.dumps  : convertit les types BSON (ObjectId, Date, etc.) en JSON
        # json.loads       : reconvertit ce JSON en dictionnaire Python standard
        # Objectif : éviter les erreurs "not JSON serializable"
        'query': json.loads(json_util.dumps(query)),

        # Nombre total de documents retournés par la requête
        # Utile pour le debug, la pagination ou l’affichage
        'count': len(results),

        # Liste des documents retournés par MongoDB
        # serialize_doc :
        # - transforme les ObjectId en string
        # - rend les documents compatibles avec jsonify
        'data': serialize_doc(results)
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    print("="*60)
    print("🚀 BoutiqueComplete1 - Flask Server")
    print("="*60)
    print("📦 Database: MongoDB - BoutiqueComplete1")
    print("🌐 Server: http://localhost:5000")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
