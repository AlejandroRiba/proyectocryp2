from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from sqlalchemy.orm import relationship
from models.Tarjeta import Tarjeta

db = getDatabase()

# Clase para los clientes
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)

    # Configuramos la relación en cascada para eliminar las tarjetas asociadas
    tarjetas = relationship('Tarjeta', backref='cliente', cascade="all, delete-orphan")

def crear_cliente_con_tarjeta(nombre, telefono, numero_tarjeta):
    # Crear el cliente
    nuevo_cliente = Cliente(nombre=nombre, telefono=telefono)
    db.session.add(nuevo_cliente)
    db.session.flush()  # Asegura que el cliente tenga un ID antes de añadir la tarjeta

    # Crear la tarjeta asociada al cliente recién creado
    tarjeta_asociada = Tarjeta(numero_tarjeta=numero_tarjeta, cliente_id=nuevo_cliente.id)
    db.session.add(tarjeta_asociada)
    
    # Confirmar ambos registros en la base de datos
    db.session.commit()
    
    return nuevo_cliente, tarjeta_asociada

def crear_cliente(nombre, telefono, tarjeta):
    nuevo_cliente = Cliente(nombre=nombre, telefono=telefono)
    db.session.add(nuevo_cliente)
    db.session.commit()
    return nuevo_cliente

def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        print(f'Cliente y sus tarjetas asociadas eliminados exitosamente.')
    else:
        print(f'Cliente con ID {cliente_id} no encontrado.')