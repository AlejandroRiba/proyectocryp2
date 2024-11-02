from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para las tarjetas de crédito
class Tarjeta(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_tarjeta = db.Column(db.String(16), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)  # Cambiado a Integer
    clave = db.Column(db.String(350), unique=True, nullable=False) #clave de la tarjeta

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

def obtener_tarjeta_por_numero(numero_tarjeta):
    tarjeta = Tarjeta.query.filter_by(numero_tarjeta=numero_tarjeta).first()
    if tarjeta:
        return tarjeta
    else:
        print(f'Tarjeta con número {numero_tarjeta} no encontrada.')
        return None
