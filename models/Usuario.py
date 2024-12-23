from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
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

    def __repr__(self):
        return f'<Usuario {self.id}>'
    
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'
    
    def __getattribute__(self, name):
        return super().__getattribute__(name)

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
    return Usuario.query.filter(Usuario.cargo.in_(['Employee', 'Fired'])) \
        .order_by(case(
            (Usuario.cargo == 'Employee', 1),
            (Usuario.cargo == 'Fired', 2),
            else_=3
        )).all()

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


def eliminar_usuario(id):
    try:
        usuario = obtener_usuario_por_id(id)
        if usuario:
            if usuario.cargo == 'Fired':
                return False, "User already deactivated."
            else:
                # Intentar eliminar el usuario
                db.session.delete(usuario)
                db.session.commit()
                print(f"Usuario {id} eliminado exitosamente.")
                return True, "User deleted successfully."
        else:
            print(f"Usuario {id} no encontrado.")
            return False, "User not found."
    except IntegrityError:
        # Si hay dependencias, limpia los campos y marca como desactivado
        db.session.rollback()  # Revertir cualquier cambio pendiente
        usuario = obtener_usuario_por_id(id)
        if usuario:
            usuario.password = ""
            usuario.cargo = "Fired"
            db.session.commit()
            print(f"Usuario {id} no se pudo eliminar, pero se desactivó correctamente.")
            return True, "User couldn't be deleted, but was deactivated."
    except Exception as e:
        db.session.rollback()
        print(f"Error al intentar eliminar el usuario {id}: {e}")
        return False, f"Error trying to delete user {id}: {e}"

