import os
import re
from flask import Blueprint, jsonify, redirect, render_template, request, session

from init import getApp
from models.Database import getDatabase
from models.Producto import Producto, crear_producto_con_variantes, delete_product, editar_producto_con_variantes, obtener_producto_por_id, obtener_productos

products_blueprint = Blueprint('products', __name__)
app = getApp()
db = getDatabase()

# Ruta para consultar productos
@products_blueprint.route('/consulta_productos', methods=['GET'])
def consulta_productos():
    username = session['username']
    productos = obtener_productos()
    return render_template('consulta_productos.html', status=username, productos=productos)
        
# Ruta para crear producto
@products_blueprint.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        id = request.form['id_product']
        nombre = request.form['nombre']
        color = request.form['color']
        precio = request.form['precio']
        categoria = request.form['tipo_producto']

        file = request.files['image']
        variantes = []
        tallas = request.form.getlist('talla')
        stocks = request.form.getlist('stock')
        # Agrupar tallas y stocks
        for talla, stock in zip(tallas, stocks):
            variantes.append({'talla': talla, 'stock': stock})
        crear_producto_con_variantes(id, nombre, color, precio, variantes, file.filename, categoria=categoria)
        #guardar la imagen del producto
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect('/consulta_productos')
    else:
        username = session['username']
        return render_template('crear_producto.html', status=username)
        
#Ruta para renderizar la plantilla de editar
@products_blueprint.route('/editar_producto/<string:id>', methods=['GET'])
def editar_producto(id):
    producto = obtener_producto_por_id(id)
    if not producto:
        return redirect('/consulta_productos')
    username = session['username']
    return render_template('editar_producto.html', producto=producto, status=username)

#Ruta para editar un producto 
@products_blueprint.route('/editar_producto_query', methods=['POST'])
def editar_producto_query():
    id = request.form['id_product']
    nombre = request.form['nombre']
    color = request.form['color']
    precio = request.form['precio']
    variantes = []
    variantes_a_eliminar = request.form.getlist('delete')
    tallas = request.form.getlist('talla')
    stocks = request.form.getlist('stock')
    ids = request.form.getlist('id_variante')
    # Agrupar tallas y stocks
    for index, (talla, stock) in enumerate(zip(tallas, stocks)):
        # Verifica si el índice existe en la lista ids
        if index < len(ids):  # Solo si hay un ID correspondiente
            id_v = ids[index]
            variantes.append({'talla': talla, 'id': id_v, 'stock': stock})
        else:
            variantes.append({'talla': talla, 'id': 0, 'stock': stock})  # ID despreciable

    if 'image' in request.files: #si si se activo la checkbox de editar
        file = request.files['image']
        lastFile = request.form['edit-image']
        nuevo_path = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
        last_path = os.path.join(app.config['UPLOAD_FOLDER'],lastFile)
        # Elimina la imagen existente si el archivo es diferente
        if os.path.isfile(last_path) and file.filename != lastFile:
            os.remove(last_path)

        # Guarda el nuevo archivo (se reemplazará si tiene el mismo nombre)
        file.save(nuevo_path)
        editar_producto_con_variantes(id,nombre,color,precio,variantes,variantes_a_eliminar, file.filename)
    else:
        editar_producto_con_variantes(id,nombre,color,precio,variantes,variantes_a_eliminar, None)

#Ruta para eliminar un producto 
@products_blueprint.route('/eliminar_producto/<string:id>', methods=['GET'])
def eliminar_producto(id):
    if not obtener_producto_por_id(id):
        redirect('/')
    
    borrado, filename = delete_product(id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if borrado and os.path.isfile(file_path): # Verificar si el archivo existe y eliminarlo
        os.remove(file_path) #elimina la imagen si la consulta de delete se ejecuta con éxito
    

@products_blueprint.route('/filtrar_productos', methods=['GET'])
def filtrar_productos():
    nombre = request.args.get('nombre', '')
    categoria = request.args.get('categoria', '')

    query = db.session.query(Producto)
    
    id_pattern = r"^[TJPAS]\d{4}$"

    if nombre:
        if re.match(id_pattern, nombre):
            # Si coincide con el patrón del ID, filtra por `id`
            query = query.filter(Producto.id == nombre)
        else:
            # Si no, filtra por `nombre`
            query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if categoria:
        if categoria == "best":
            query = query.order_by(Producto.salidas.desc()).limit(5)
        else:
            query = query.filter(Producto.categoria == categoria)

    productos = query.all()
        
        # Convertimos los productos en un formato adecuado para JSON
    productos_data = [{
        "id": producto.id,
        "archivo": producto.archivo,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "categoria": producto.categoria,
        "variantes": [{"talla": variante.talla, "stock": variante.stock} for variante in producto.variantes] if producto.variantes else [{"talla": "", "stock": 0}],
        "color": producto.color
    } for producto in productos]

    return jsonify({"productos": productos_data})
    