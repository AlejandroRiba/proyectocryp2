from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

class DetalleTransaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaccion_id = db.Column(db.String(10), db.ForeignKey('transaccion.id'), nullable=False)
    producto_id = db.Column(db.String(10), db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

def crear_detalle_transaccion(transaccion_id, producto_id, cantidad):
    nuevo_detalle = DetalleTransaccion(transaccion_id=transaccion_id, producto_id=producto_id, cantidad=cantidad)
    db.session.add(nuevo_detalle)
    db.session.commit()
    return nuevo_detalle