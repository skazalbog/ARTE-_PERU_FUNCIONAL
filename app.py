import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

# Inicializar la app, base de datos y extensiones
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Una sola base de datos
app.config['UPLOAD_FOLDER'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_vendedor = db.Column(db.Boolean, default=False)  # Para diferenciar usuarios de vendedores

# Modelo de producto
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300))

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializar base de datos
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print('Base de datos inicializada.')

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        is_vendedor = 'vendedor' in request.form

        new_user = User(username=username, email=email, password=hashed_password, is_vendedor=is_vendedor)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario registrado correctamente', 'success')
            return redirect(url_for('login'))
        except:
            flash('Error al registrar usuario. Verifica tus datos.', 'danger')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# Dashboard del administrador
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_vendedor:
        products = Product.query.all()
        return render_template('admin/dashboard.html', products=products)
    else:
        flash('Acceso denegado. No eres vendedor.', 'danger')
        return redirect(url_for('user_home'))

# Gestión de productos
@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_vendedor:
        flash('Acceso denegado. No eres vendedor.', 'danger')
        return redirect(url_for('user_home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image = None

        # Subir imagen si se incluye
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image = filename

        new_product = Product(name=name, description=description, price=price, image=image)
        db.session.add(new_product)
        db.session.commit()
        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    if not current_user.is_vendedor:
        flash('Acceso denegado. No eres vendedor.', 'danger')
        return redirect(url_for('user_home'))

    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])

        # Subir nueva imagen si se incluye
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image = filename

        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    if not current_user.is_vendedor:
        flash('Acceso denegado. No eres vendedor.', 'danger')
        return redirect(url_for('user_home'))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('dashboard'))

# Rutas de usuario
@app.route('/')
def user_home():
    products = Product.query.all()
    return render_template('user/home.html', products=products)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Producto no encontrado", 404

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'id': product.id,
        'name': product.name,
        'price': product.price
    })
    session.modified = True
    return redirect(url_for('user_cart'))

@app.route('/cart')
def user_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('user/cart.html', cart=cart, total=total)

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('user_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def user_checkout():
    if request.method == 'POST':
        session.pop('cart', None)
        flash('Compra realizada con éxito.', 'success')
        return redirect(url_for('user_home'))
    return render_template('user/checkout.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
