from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase

db = getDatabase()

# Clase para los reportes
class Reporte(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    empleado_id = db.Column(db.String(10), db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

def crear_reporte(empleado_id, fecha):
    nuevo_reporte = Reporte(empleado_id=empleado_id, fecha=fecha)
    db.session.add(nuevo_reporte)
    db.session.commit()
    return nuevo_reporte

def obtener_reportes_por_empleado(empleado_id):
    reportes = Reporte.query.filter_by(empleado_id=empleado_id).all()
    return reportes