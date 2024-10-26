from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para las tarjetas de crédito
class Tarjeta(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_tarjeta = db.Column(db.String(16), unique=True, nullable=False)
    cliente_id = db.Column(db.String(10), db.ForeignKey('cliente.id'), nullable=False)

def crear_tarjeta(numero_tarjeta, cliente_id):
    nueva_tarjeta = Tarjeta(numero_tarjeta=numero_tarjeta, cliente_id=cliente_id)
    db.session.add(nueva_tarjeta)
    db.session.commit()
    return nueva_tarjeta

def eliminar_tarjeta(tarjeta_id):
    tarjeta = Tarjeta.query.get(tarjeta_id)
    if tarjeta:
        db.session.delete(tarjeta)
        db.session.commit()
        print(f'Tarjeta eliminada exitosamente.')
    else:
        print(f'Tarjeta con ID {tarjeta_id} no encontrada.')