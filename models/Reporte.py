from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para los reportes
class Reporte(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    empleado_id = db.Column(db.String(10), db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    firma = db.Column(db.String(300), nullable=False)