import sqlite3

# Función para conectarse a la base de datos
def get_db_connection():
    conn = sqlite3.connect('ecommerce.db')  # Crea/abre la base de datos
    conn.row_factory = sqlite3.Row         # Permite acceso a los datos como diccionarios
    return conn

# Función para inicializar la base de datos
def init_db():
    conn = get_db_connection()
    with conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT
        );
        ''')
    conn.close()
    print("Base de datos inicializada correctamente.")



# Crear un producto
def create_product(name, description, price, image=None):
    conn = get_db_connection()
    with conn:
        conn.execute('''
            INSERT INTO products (name, description, price, image)
            VALUES (?, ?, ?, ?)
        ''', (name, description, price, image))
    conn.close()

# Leer todos los productos
def get_all_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return products

# Leer un producto por ID
def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return product

# Actualizar un producto
def update_product(product_id, name, description, price, image=None):
    conn = get_db_connection()
    with conn:
        conn.execute('''
            UPDATE products
            SET name = ?, description = ?, price = ?, image = ?
            WHERE id = ?
        ''', (name, description, price, image, product_id))
    conn.close()

# Eliminar un producto
def delete_product(product_id):
    conn = get_db_connection()
    with conn:
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.close()
