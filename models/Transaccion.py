from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from models.DetalleTransaccion import DetalleTransaccion

db = getDatabase()

# Clase para las transacciones
class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.String(10), db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)

def crear_transaccion(empleado_id, fecha, monto):
    nueva_transaccion = Transaccion(empleado_id=empleado_id, fecha=fecha, monto=monto)
    db.session.add(nueva_transaccion)
    db.session.commit()
    return nueva_transaccion

def crear_transaccion_con_detalles(empleado_id, fecha, monto, productos):
    """
    productos: lista de diccionarios con 'producto_id' y 'cantidad' para cada producto.
    Ejemplo: [{"producto_id": 1, "cantidad": 2}, {"producto_id": 2, "cantidad": 1}]
    """
    try:
        # Crear la transacción principal
        nueva_transaccion = Transaccion(empleado_id=empleado_id, fecha=fecha, monto=monto)
        db.session.add(nueva_transaccion)
        db.session.flush()  # Obtiene el ID de la transacción antes de agregar los detalles
        
        # Crear detalles de transacción para cada producto en la lista
        for producto in productos:
            nuevo_detalle = DetalleTransaccion(
                transaccion_id=nueva_transaccion.id,
                producto_id=producto['producto_id'],
                cantidad=producto['cantidad']
            )
            db.session.add(nuevo_detalle)
        
        # Confirmar toda la transacción y sus detalles
        db.session.commit()
        return nueva_transaccion
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear la transacción con detalles: {e}")
        return None