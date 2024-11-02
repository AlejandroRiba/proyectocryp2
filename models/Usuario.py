from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models.Database import getDatabase

db = getDatabase()

class Usuario(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    cargo = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    publickey = db.Column(db.String(620), nullable=False)

def crear_usuario(id, nombre, apellido, email, phone, password, key):
    try:
        if id == 'admin':
            usuario = obtener_usuario_por_id(id)
            editar_usuario(usuario, nombre, apellido, email, phone, password, key)
        else:
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

def obtener_empleados():
    return Usuario.query.filter_by(cargo='Employee').all()

def obtener_password(id):
    usuario = obtener_usuario_por_id(id)
    return usuario.password

def obtener_pub_key(id):
    usuario = obtener_usuario_por_id(id)
    return usuario.publickey

def obtener_usuario_por_id(id):
    return Usuario.query.get(id)

def editar_usuario(usuario, nombre, apellido, email, phone, password, key): #edita el usuario habiendo hecho la consulta antes
    if usuario:
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.email = email
        usuario.phone = phone
        if password != None:
            usuario.password = password
        if key != None:
            usuario.publickey = key
        db.session.commit()
        return True
    else:
        return False
    
def confirma_existencia_admin():
    usuario = obtener_usuario_por_id('admin')
    if usuario:
        if usuario.password != 'admin':
            return True 
        else:
            return False #si existe el usuario admin pero aún no ha iniciado sesión para cambiar de contraseña
    else:
        return False

