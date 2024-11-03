from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from sqlalchemy.orm import relationship

db = getDatabase()

# Clase para los productos
class Producto(db.Model):
    id = db.Column(db.String(6), primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    salidas = db.Column(db.Integer, nullable=False)
    archivo = db.Column(db.String(10), nullable=False)
    categoria = db.Column(db.String(11), nullable=False)
    # Relación con ProductoVariante
    variantes = relationship('ProductoVariante', backref='producto', cascade="all, delete-orphan")

class ProductoVariante(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.String(6), db.ForeignKey('producto.id'), nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Función para crear un producto con variantes
def crear_producto_con_variantes(id, nombre, color, precio, variantes, archivo, categoria):
    # Crear el producto principal
    nuevo_producto = Producto(id=id, nombre=nombre, color=color, precio=precio, salidas=0, archivo=archivo, categoria=categoria)
    db.session.add(nuevo_producto)
    db.session.flush()  # Asegura que el producto tenga un ID antes de añadir las variantes

    # Crear variantes asociadas al producto recién creado
    variantes_objs = [
        ProductoVariante(talla=variante['talla'], stock=variante['stock'], producto_id=nuevo_producto.id)
        for variante in variantes
    ]
    db.session.add_all(variantes_objs)

    # Confirmar ambos registros en la base de datos
    db.session.commit()
    
    return nuevo_producto, variantes_objs


def crear_producto(id, nombre, color, precio, archivo, categoria):
    nuevo_producto = Producto(id=id, nombre=nombre, color=color, precio=precio, salidas=0, archivo=archivo, categoria=categoria)
    db.session.add(nuevo_producto)
    db.session.commit()
    return nuevo_producto

# Función para eliminar un producto y sus variantes
def delete_product(producto_id):
    producto = Producto.query.get(producto_id)
    archivo = producto.archivo
    if producto:
        db.session.delete(producto)
        db.session.commit()
        return True, archivo
    else:
        return False, None #error/producto no encontrado

#Funcion para editar un producto y sus variantes
def editar_producto_con_variantes(producto_id, nombre, color, precio, variantes, eliminar_variantes_ids, archivo):
    # Obtener el producto existente
    producto = Producto.query.get(producto_id)

    if not producto:
        raise ValueError("Producto no encontrado")

    # Actualizar el producto principal
    producto.nombre = nombre
    producto.color = color
    producto.precio = precio
    if archivo != None:
        producto.archivo = archivo
    
    # Actualizar las variantes existentes
    for variante in variantes:
        # Buscar la variante por ID
        variante_existente = ProductoVariante.query.get(variante['id'])
        if variante_existente:
            variante_existente.talla = variante['talla']
            variante_existente.stock = variante['stock']
        else:
            nuevaVariante = ProductoVariante(talla=variante['talla'], stock=variante['stock'], producto_id=producto_id)
            db.session.add(nuevaVariante)
    
    # Eliminar variantes que ya no son necesarias
    for variante_id in eliminar_variantes_ids:
        variante_a_eliminar = ProductoVariante.query.get(variante_id)
        if variante_a_eliminar:
            db.session.delete(variante_a_eliminar)

    # Confirmar los cambios en la base de datos
    db.session.commit()


def obtener_productos():
    return Producto.query.all()

def mas_vendidos():
    return Producto.query.order_by(Producto.salidas.desc()).limit(5).all()

def obtener_producto_por_id(id):
    return Producto.query.get(id)

# Consultar stock de una variante específica
def obtener_stock_variante(variante_id):
    variante = ProductoVariante.query.get(variante_id)
    if variante:
        return variante.stock
    else:
        return None  # Variante no encontrada

# Modificar stock de una variante específica
def modificar_stock_variante(variante_id, nuevo_stock):
    variante = ProductoVariante.query.get(variante_id)
    if variante:
        variante.stock = nuevo_stock
        db.session.commit()
        return variante
    else:
        return None  # Variante no encontrada

# Consultar salidas de un producto específico
def obtener_salidas_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        return producto.salidas
    else:
        return None  # Producto no encontrado

# Modificar salidas de un producto específico
def modificar_salidas_producto(producto_id, nuevas_salidas):
    producto = Producto.query.get(producto_id)
    if producto:
        producto.salidas = nuevas_salidas
        db.session.commit()
        return producto
    else:
        return None  # Producto no encontrado

# Consultar variante por producto_id y talla
def obtener_variante_por_id_y_talla(producto_id, talla):
    variante = ProductoVariante.query.filter_by(producto_id=producto_id, talla=talla).first()
    return variante if variante else None  # Devuelve la variante si existe, o None si no se encuentra

# Consultar todas las variantes por producto_id
def obtener_variantes_por_producto_id(producto_id):
    variantes = ProductoVariante.query.filter_by(producto_id=producto_id).all()
    if len(variantes) == 0:
        return []
    elif len(variantes) == 1:
        return variantes[0]
    else:
        return variantes 