from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages and sessions

# Simple user storage (in production, use a proper database)
USERS_FILE = 'users.json'
ORDERS_FILE = 'orders.json'

# Expanded product catalog with categories
PRODUCTS = {
    'students': [
        {"id": 1, "name": "HP Pavilion 14", "price": "45,999", "image": "product1.jpg", "specs": "Intel i5, 8GB RAM, 256GB SSD", "description": "Perfect for students with long battery life and lightweight design.", "rating": 4.5, "reviews": 128},
        {"id": 2, "name": "ASUS VivoBook 15", "price": "42,999", "image": "product2.jpg", "specs": "AMD Ryzen 5, 8GB RAM, 512GB SSD", "description": "Budget-friendly laptop ideal for everyday tasks and studying.", "rating": 4.3, "reviews": 95},
        {"id": 3, "name": "Lenovo IdeaPad 3", "price": "38,999", "image": "product3.jpg", "specs": "Intel i3, 4GB RAM, 1TB HDD", "description": "Affordable option for basic computing needs and note-taking.", "rating": 4.1, "reviews": 76},
        {"id": 4, "name": "Acer Aspire 5", "price": "48,999", "image": "product4.jpg", "specs": "Intel i5, 8GB RAM, 512GB SSD", "description": "Reliable performance for students with excellent portability.", "rating": 4.4, "reviews": 112},
    ],
    'developers': [
        {"id": 5, "name": "MacBook Pro 14", "price": "1,89,999", "image": "product5.jpg", "specs": "M2 Pro, 16GB RAM, 512GB SSD", "description": "Ultimate coding machine with exceptional performance and display.", "rating": 4.8, "reviews": 203},
        {"id": 6, "name": "Dell XPS 13", "price": "1,25,999", "image": "product6.jpg", "specs": "Intel i7, 16GB RAM, 1TB SSD", "description": "Premium ultrabook perfect for development work.", "rating": 4.6, "reviews": 156},
        {"id": 7, "name": "ThinkPad X1 Carbon", "price": "1,45,999", "image": "product7.jpg", "specs": "Intel i7, 16GB RAM, 512GB SSD", "description": "Business-grade laptop with excellent keyboard for coding.", "rating": 4.7, "reviews": 189},
        {"id": 8, "name": "HP ZBook Studio", "price": "1,65,999", "image": "product8.jpg", "specs": "Intel i9, 32GB RAM, 1TB SSD", "description": "Workstation-class performance for heavy development tasks.", "rating": 4.5, "reviews": 87},
    ],
    'gamers': [
        {"id": 9, "name": "ASUS ROG Strix G15", "price": "89,999", "image": "product9.jpg", "specs": "AMD Ryzen 7, RTX 3060, 16GB RAM", "description": "High-performance gaming laptop with RGB lighting.", "rating": 4.6, "reviews": 234},
        {"id": 10, "name": "MSI Katana GF66", "price": "78,999", "image": "product10.jpg", "specs": "Intel i7, RTX 3050 Ti, 16GB RAM", "description": "Gaming laptop with excellent cooling and performance.", "rating": 4.4, "reviews": 167},
        {"id": 11, "name": "Acer Predator Helios", "price": "95,999", "image": "product11.jpg", "specs": "Intel i7, RTX 3070, 16GB RAM", "description": "Premium gaming experience with high refresh rate display.", "rating": 4.7, "reviews": 198},
        {"id": 12, "name": "Lenovo Legion 5", "price": "85,999", "image": "product12.jpg", "specs": "AMD Ryzen 5, RTX 3060, 16GB RAM", "description": "Balanced gaming laptop with great price-to-performance ratio.", "rating": 4.5, "reviews": 145},
    ],
    'professionals': [
        {"id": 13, "name": "MacBook Air M2", "price": "1,19,999", "image": "product13.jpg", "specs": "M2 Chip, 8GB RAM, 256GB SSD", "description": "Ultra-portable with exceptional battery life for professionals.", "rating": 4.7, "reviews": 312},
        {"id": 14, "name": "Surface Laptop 5", "price": "1,35,999", "image": "product14.jpg", "specs": "Intel i7, 16GB RAM, 512GB SSD", "description": "Premium Windows laptop with touchscreen display.", "rating": 4.4, "reviews": 98},
        {"id": 15, "name": "HP EliteBook 840", "price": "1,25,999", "image": "product15.jpg", "specs": "Intel i7, 16GB RAM, 512GB SSD", "description": "Business laptop with enterprise security features.", "rating": 4.3, "reviews": 76},
        {"id": 16, "name": "Dell Latitude 9520", "price": "1,55,999", "image": "product16.jpg", "specs": "Intel i7, 16GB RAM, 1TB SSD", "description": "Premium business laptop with 5G connectivity.", "rating": 4.5, "reviews": 134},
    ]
}

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

def get_all_products():
    """Get all products as a flat list with category info"""
    all_products = []
    for category, products in PRODUCTS.items():
        for product in products:
            product_copy = product.copy()
            product_copy['category'] = category
            all_products.append(product_copy)
    return all_products

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    for category, products in PRODUCTS.items():
        for product in products:
            if product['id'] == product_id:
                product_copy = product.copy()
                product_copy['category'] = category
                return product_copy
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shop')
@app.route('/shop/<category>')
def shop(category=None):
    search_query = request.args.get('search', '').strip()
    
    if category and category in PRODUCTS:
        products = PRODUCTS[category]
        category_title = {
            'students': 'Laptops for Students',
            'developers': 'Laptops for Developers',
            'gamers': 'Gaming Laptops',
            'professionals': 'Professional Laptops'
        }.get(category, 'All Laptops')
    else:
        # Show all products if no category specified
        products = get_all_products()
        category_title = 'All Laptops'
    
    # Filter by search query if provided
    if search_query:
        filtered_products = []
        for product in products:
            if (search_query.lower() in product['name'].lower() or 
                search_query.lower() in product['description'].lower() or
                search_query.lower() in product['specs'].lower()):
                filtered_products.append(product)
        products = filtered_products
        if search_query:
            category_title = f'Search results for "{search_query}"'
    
    return render_template('shop.html', products=products, category_title=category_title, 
                         current_category=category, search_query=search_query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('shop'))
    
    # Get related products from the same category
    related_products = PRODUCTS.get(product['category'], [])[:3]
    
    return render_template('product_detail.html', product=product, related_products=related_products)

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            cart_item = {
                'product': product,
                'quantity': item['quantity'],
                'subtotal': int(product['price'].replace(',', '')) * item['quantity']
            }
            cart_items.append(cart_item)
            total += cart_item['subtotal']
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product already in cart
    for item in session['cart']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        session['cart'].append({'product_id': product_id, 'quantity': quantity})
    
    session.modified = True
    flash('Product added to cart!', 'success')
    return redirect(request.referrer or url_for('shop'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    
    if 'cart' in session:
        for item in session['cart']:
            if item['product_id'] == product_id:
                if quantity <= 0:
                    session['cart'].remove(item)
                else:
                    item['quantity'] = quantity
                break
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.form.get('product_id'))
    
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True
        flash('Product removed from cart', 'info')
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if not session.get('user_email'):
        flash('Please login to checkout', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('cart'):
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = get_product_by_id(item['product_id'])
        if product:
            cart_item = {
                'product': product,
                'quantity': item['quantity'],
                'subtotal': int(product['price'].replace(',', '')) * item['quantity']
            }
            cart_items.append(cart_item)
            total += cart_item['subtotal']
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    if not session.get('user_email'):
        return redirect(url_for('login'))
    
    if not session.get('cart'):
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    # Create order
    order = {
        'id': len(load_orders()) + 1,
        'user_email': session['user_email'],
        'items': session['cart'].copy(),
        'total': sum(int(get_product_by_id(item['product_id'])['price'].replace(',', '')) * item['quantity'] 
                    for item in session['cart']),
        'date': datetime.now().isoformat(),
        'status': 'confirmed'
    }
    
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    
    # Clear cart
    session['cart'] = []
    session.modified = True
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_confirmation', order_id=order['id']))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    orders = load_orders()
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order or order['user_email'] != session.get('user_email'):
        flash('Order not found', 'danger')
        return redirect(url_for('home'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signin':
            email = request.form['email']
            password = request.form['password']
            users = load_users()
            
            if email in users and users[email]['password'] == password:
                session['user_email'] = email
                session['username'] = users[email].get('username', email.split('@')[0])
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')
        
        elif action == 'signup':
            email = request.form['signup_email']
            password = request.form['signup_password']
            confirm_password = request.form['confirm_password']
            username = request.form['username']
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
            else:
                users = load_users()
                if email in users:
                    flash('Email already exists', 'danger')
                else:
                    users[email] = {
                        'password': password,
                        'username': username
                    }
                    save_users(users)
                    session['user_email'] = email
                    session['username'] = username
                    flash('Account created successfully!', 'success')
                    return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/api/cart_count')
def cart_count():
    """API endpoint to get cart item count"""
    cart = session.get('cart', [])
    count = sum(item['quantity'] for item in cart)
    return jsonify({'count': count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



