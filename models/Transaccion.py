from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from models.DetalleTransaccion import DetalleTransaccion

db = getDatabase()

# Clase para las transacciones
class Transaccion(db.Model):
    __tablename__ = 'transaccion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.String(10), db.ForeignKey('usuario.id'), nullable=False)
    tarjeta_id = db.Column(db.Integer, db.ForeignKey('tarjeta.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    # Definición de relaciones
    cliente = db.relationship('Cliente', backref='transacciones')
    tarjeta = db.relationship('Tarjeta', backref='transacciones')
    empleado = db.relationship('Usuario', backref='transacciones')

def crear_transaccion(empleado_id, fecha, monto, tarjeta_id, cliente_id):
    nueva_transaccion = Transaccion(empleado_id=empleado_id, fecha=fecha, monto=monto, tarjeta_id=tarjeta_id, cliente_id=cliente_id)
    db.session.add(nueva_transaccion)
    db.session.commit()
    return nueva_transaccion

def crear_transaccion_con_detalles(empleado_id, fecha, monto, productos, tarjeta_id, cliente_id):
    """
    productos: lista de diccionarios con 'producto_id' y 'cantidad' para cada producto.
    Ejemplo: [{"producto_id": 1, "cantidad": 2}, {"producto_id": 2, "cantidad": 1}]
    """
    try:
        # Crear la transacción principal
        nueva_transaccion = Transaccion(empleado_id=empleado_id, fecha=fecha, monto=monto, tarjeta_id=tarjeta_id, cliente_id=cliente_id)
        db.session.add(nueva_transaccion)
        db.session.flush()  # Obtiene el ID de la transacción antes de agregar los detalles
        
        # Crear detalles de transacción para cada producto en la lista
        for producto in productos:
            nuevo_detalle = DetalleTransaccion(
                transaccion_id=nueva_transaccion.id,
                producto_id=producto['id'],
                cantidad=producto['cantidad'],
                talla = producto['talla']
            )
            db.session.add(nuevo_detalle)
        
        # Confirmar toda la transacción y sus detalles
        db.session.commit()
        return nueva_transaccion
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear la transacción con detalles: {e}")
        return None
    

def consulta_transacciones():
    transacciones = Transaccion.query.all()
    if not transacciones:
        return None
    return transacciones


def transacciones_por_empleado(id):
    transacciones = Transaccion.query.filter_by(empleado_id = id).all()
    if transacciones:
        return transacciones
    else:
        return None