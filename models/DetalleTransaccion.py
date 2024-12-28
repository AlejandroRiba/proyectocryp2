from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

class DetalleTransaccion(db.Model):
    __tablename__ = 'detalle_transaccion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaccion_id = db.Column(db.Integer, db.ForeignKey('transaccion.id'), nullable=False)
    producto_id = db.Column(db.String(6), db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    talla = db.Column(db.String(10), nullable=False)

def crear_detalle_transaccion(transaccion_id, producto_id, cantidad):
    nuevo_detalle = DetalleTransaccion(transaccion_id=transaccion_id, producto_id=producto_id, cantidad=cantidad)
    db.session.add(nuevo_detalle)
    db.session.commit()
    return nuevo_detalle