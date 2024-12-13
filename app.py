import os
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, create_product, get_all_products, get_product_by_id, update_product, delete_product

app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'static/uploads'  # Carpeta donde se guardarán las imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.cli.command('init-db')
def init_db_command():
    """Inicializa la base de datos."""
    init_db()
    print('Base de datos inicializada.')


# Rutas para el Administrador
@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Ruta para listar productos
@app.route('/admin/products')
def admin_products():
    products = get_all_products()
    return render_template('admin/products.html', products=products)

# Ruta para agregar un producto
# Ruta para agregar un producto
@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        create_product(name, description, price)
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html')

# Ruta para editar un producto
@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    product = get_product_by_id(product_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        update_product(product_id, name, description, price)
        return redirect(url_for('admin_products'))
    return render_template('admin/edit_product.html', product=product)

# Ruta para eliminar un producto
@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    delete_product(product_id)
    return redirect(url_for('admin_products'))


# Ruta para listar productos (Inicio del usuario)
@app.route('/')
def user_home():
    products = get_all_products()
    return render_template('user/home.html', products=products)

# Ruta para agregar un producto al carrito
@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Producto no encontrado", 404
    
    # Inicializar el carrito si no existe
    if 'cart' not in session:
        session['cart'] = []

    # Agregar el producto al carrito
    session['cart'].append({
        'id': product['id'],
        'name': product['name'],
        'price': product['price']
    })
    session.modified = True  # Indicar que la sesión cambió
    return redirect(url_for('user_cart'))

# Ruta para mostrar el carrito
@app.route('/cart')
def user_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('user/cart.html', cart=cart, total=total)

# Ruta para vaciar el carrito
@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)  # Eliminar el carrito de la sesión
    return redirect(url_for('user_cart'))

# Ruta para simular el pago
@app.route('/checkout', methods=['GET', 'POST'])
def user_checkout():
    if request.method == 'POST':
        session.pop('cart', None)  # Vaciar el carrito después del pago
        return render_template('user/checkout_success.html')
    return render_template('user/checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
