from datetime import datetime
import json
from flask import Blueprint, redirect, render_template, request, session

from models.Cliente import crear_cliente_con_tarjeta
from models.Producto import mas_vendidos, modificar_salidas_producto, modificar_stock_variante, obtener_producto_por_id
from models.Producto import obtener_salidas_producto, obtener_stock_variante, obtener_variante_por_id_y_talla, obtener_variantes_por_producto_id
from models.Tarjeta import obtener_clave_tarjeta
from models.Transaccion import consulta_transacciones, crear_transaccion_con_detalles, transacciones_por_empleado
from models.Usuario import obtener_usuario_por_id
from pyFunctions import mainfunc

clients_transactions_blueprint = Blueprint('clients_transactions', __name__)

# Ruta para consultar clientes
@clients_transactions_blueprint.route('/consulta_clientes', methods=['GET'])
def consulta_clientes():
    username = session['username']
    return render_template('consulta_clientes.html', status=username)
        
# Ruta para crear/registrar un ventas
@clients_transactions_blueprint.route('/registra_venta', methods=['GET'])
def registra_venta():
    username = session['username']
    productos = mas_vendidos() #aplica un filtro de productos más vendidos para que no se tenga una tabla muy extensa 
    return render_template('registra_venta.html', status=username, productos=productos)
        
        
@clients_transactions_blueprint.route('/procesar_venta', methods=['POST'])
def procesar_venta():
    data = request.form

    productos = json.loads(data.get('seleccionados'))
    nombre = data['nombre']
    apellido = data['apellido']
    numero = data['numero']
    card = data['card']
    username = session['username']
    monto = 0
    
    tarjeta, cliente = crear_cliente_con_tarjeta(nombre=nombre, apellido=apellido, telefono=numero, numero_tarjeta=card)

    if not (tarjeta and cliente): # Si no se creo correctamnete el cliente
        return redirect('/')

    for producto in productos:
        item = obtener_producto_por_id(producto["id"])
        monto += item.precio * int(producto['cantidad'])

        # Disminuir stock de la variante seleccionada según la cantidad vendida
        try:
            variante = obtener_variante_por_id_y_talla(producto["id"], producto['talla'])
            stock = obtener_stock_variante(variante.id)
            modificar_stock_variante(variante.id, stock - producto['cantidad'])
        except Exception as e:
            variante = obtener_variantes_por_producto_id(producto["id"])
            stock = obtener_stock_variante(variante.id)
            modificar_stock_variante(variante.id, stock - producto['cantidad'])

        salidas = obtener_salidas_producto(producto["id"])
        modificar_salidas_producto(producto["id"], salidas + producto['cantidad'])
    crear_transaccion_con_detalles(empleado_id=username, fecha=datetime.now(), monto=monto, productos=productos, tarjeta_id=tarjeta.id, cliente_id=cliente.id)
    return redirect('/')

# Ruta para consultar ventas
@clients_transactions_blueprint.route('/consulta_venta', methods=['GET'])
def consulta_venta():
    username = session['username']
    employee = obtener_usuario_por_id(username)

    if employee.cargo == 'Employee':
        transacciones = transacciones_por_empleado(username).all()
        return render_template('consulta_venta.html', status=username, transacciones=transacciones)

    private_key = session['private_key']
    transacciones = consulta_transacciones()
    for transaccion in transacciones:
        llave_cifrada = obtener_clave_tarjeta(transaccion.tarjeta.numero_tarjeta)
        tarjeta = mainfunc.descifrar_tarjeta(transaccion.tarjeta.numero_tarjeta, private_key, llave_cifrada)
        transaccion.tarjeta.numero_tarjeta = tarjeta
                
    return render_template('consulta_venta.html', status=username, transacciones=transacciones)
     