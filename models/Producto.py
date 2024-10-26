from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para los productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)

def crear_producto(nombre, precio):
    nuevo_producto = Producto(nombre=nombre, precio=precio)
    db.session.add(nuevo_producto)
    db.session.commit()
    return nuevo_producto