from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    cargo = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    publickey = db.Column(db.String(250), nullable=False)

def crear_usuario(id, nombre, apellido, email, phone, password, key):
    try:
        nuevo_usuario = Usuario(id=id, nombre=nombre, apellido=apellido, email=email, phone=phone, cargo='Employee', password=password, publickey=key)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback() #Deshace algún cambion no confirmado en la base de datos
        print(f'Usuario ya existe.')
        return False
    except Exception as e:
        db.session.rollback()
        print(f'Error {e}')
        return False

def obtener_usuarios():
    return Usuario.query.all()

def obtener_usuario_por_id(id):
    return Usuario.query.get(id)
