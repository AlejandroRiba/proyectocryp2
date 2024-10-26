from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para las tarjetas de crédito
class Tarjeta(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    numero_tarjeta = db.Column(db.String(16), unique=True, nullable=False)
    cliente_id = db.Column(db.String(10), db.ForeignKey('cliente.id'), nullable=False)
