from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para los clientes
class Cliente(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)


