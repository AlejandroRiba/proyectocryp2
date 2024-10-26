from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

class DetalleTransaccion(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    transaccion_id = db.Column(db.String(10), db.ForeignKey('transaccion.id'), nullable=False)
    producto_id = db.Column(db.String(10), db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

# Clase para los reportes
class Reporte(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    empleado_id = db.Column(db.String(10), db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    firma = db.Column(db.String(250), nullable=False)