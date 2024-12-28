from flask_sqlalchemy import SQLAlchemy 
from models.Database import getDatabase
from sqlalchemy.orm import relationship
from models.Tarjeta import Tarjeta
from pyFunctions.mainfunc import cifrar_tarjeta

db = getDatabase()

# Clase para los clientes
class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15),  nullable=False)

    # Configuramos la relación en cascada para eliminar las tarjetas asociadas
    tarjetas = relationship('Tarjeta', backref='cliente', cascade="all, delete-orphan")

def crear_cliente_con_tarjeta(nombre, apellido, telefono, numero_tarjeta):
    try:
        # Verificar si el cliente ya existe
        cliente_existente = Cliente.query.filter_by(nombre=nombre, apellido=apellido, telefono=telefono).first()
        mensaje = ""
        if cliente_existente:
            print('Cliente existente')
            # Crear y asociar la tarjeta al cliente existente 
            tarjeta, clave = cifrar_tarjeta(numero_tarjeta)
            nuevo_cliente = cliente_existente
            nueva_tarjeta = Tarjeta(numero_tarjeta=tarjeta, cliente_id=cliente_existente.id, clave=clave)
            db.session.add(nueva_tarjeta)
        else:
            # Crear un nuevo cliente y asociar la tarjeta
            nuevo_cliente = Cliente(nombre=nombre, apellido=apellido, telefono=telefono)
            db.session.add(nuevo_cliente)
            db.session.flush()  # Asegura que el cliente tenga un ID antes de añadir la tarjeta
            
            tarjeta, clave = cifrar_tarjeta(numero_tarjeta)
            nueva_tarjeta = Tarjeta(numero_tarjeta=tarjeta, cliente_id=nuevo_cliente.id, clave=clave)
            db.session.add(nueva_tarjeta)
        
        # Confirmar todos los cambios en la base de datos
        db.session.commit()
        return nueva_tarjeta, nuevo_cliente
    except Exception as e:
        db.session.rollback()  # Revierte la transacción en caso de error
        print(f"Error al crear el cliente y la tarjeta: {e}")
        mensaje = f"Error al crear el cliente y la tarjeta: {e}"
        return False, mensaje


def crear_cliente(nombre, apellido, telefono):
    try:
        nuevo_cliente = Cliente(nombre=nombre, apellido=apellido, telefono=telefono)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear el cliente: {e}")
        return False

def eliminar_cliente(cliente_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if cliente:
            db.session.delete(cliente)
            db.session.commit()
            print(f'Cliente y sus tarjetas asociadas eliminados exitosamente.')
            return True
        else:
            print(f'Cliente con ID {cliente_id} no encontrado.')
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el cliente: {e}")
        return False

def obtener_cliente_por_tel(tel):
    cliente =  Cliente.query.filter_by(telefono=tel).first()
    if cliente:
        return cliente
    else:
        print(f'Cliente con número {tel} no encontrado.')
        return None