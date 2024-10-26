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
    # Relación con ProductoVariante
    variantes = relationship('ProductoVariante', backref='producto', cascade="all, delete-orphan")

class ProductoVariante(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.String(6), db.ForeignKey('producto.id'), nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Función para crear un producto con variantes
def crear_producto_con_variantes(id, nombre, color, precio, variantes, archivo):
    # Crear el producto principal
    nuevo_producto = Producto(id=id, nombre=nombre, color=color, precio=precio, salidas=0, archivo=archivo)
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


def crear_producto(id, nombre, color, precio, archivo):
    nuevo_producto = Producto(id=id, nombre=nombre, color=color, precio=precio, salidas=0, archivo=archivo)
    db.session.add(nuevo_producto)
    db.session.commit()
    return nuevo_producto

# Función para eliminar un producto y sus variantes
def eliminar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if producto:
        db.session.delete(producto)
        db.session.commit()
        return True
    else:
        return False #error/producto no encontrado

def obtener_productos():
    return Producto.query.all()