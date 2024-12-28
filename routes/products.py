import os
import re
from flask import Blueprint, jsonify, redirect, render_template, request, session
from sqlalchemy import or_, desc
from init import getApp
from models.Database import getDatabase
from models.Producto import Producto, crear_producto_con_variantes, delete_product, editar_producto_con_variantes, obtener_producto_por_id, productos_paginados

products_blueprint = Blueprint('products', __name__)
app = getApp()
db = getDatabase()

# Ruta para consultar productos
@products_blueprint.route('/consulta_productos', methods=['GET'])
def consulta_productos():
    username = session['username']
    productos = productos_paginados()
    return render_template('consulta_productos.html', status=username, productos=productos, page=1, per_page=4, consulta="producto")
        
# Ruta para crear producto
@products_blueprint.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        try:
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

            # Respuesta positiva
            return jsonify({'success': True, 'message': 'Product created successfully.', 'destino': 'consulta_productos'}), 200

        except ValueError as e:
            return jsonify({'success': False, 'message': 'Internal server error.', 'destino': None}), 400 
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
    try:
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

        # Respuesta positiva
        return jsonify({'success': True, 'message': 'Product updated successfully.', 'destino': 'consulta_productos'}), 200

    except ValueError as e:
        return jsonify({'success': False, 'message': 'Internal server error.', 'destino': None}), 400   

#Ruta para eliminar un producto 
@products_blueprint.route('/eliminar_producto', methods=['GET'])
def eliminar_producto():
    username = session['username']
    if username == 'admin':
        id = request.args.get('id', '') #obtengo el id de la solicitud fetch

        borrado, filename = delete_product(id) #aquí se intenta borrar el elemento
        if borrado:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if borrado and os.path.isfile(file_path): # Verificar si el archivo existe y eliminarlo
                os.remove(file_path) #elimina la imagen si la consulta de delete se ejecuta con éxito
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    else:
        return jsonify({"success": False})

@products_blueprint.route('/filtrar_productos', methods=['GET'])
def filtrar_productos():
    username = session['username']
    nombre = request.args.get('nombre', '')
    categoria = request.args.get('categoria', '')
    consulta = request.args.get('consulta', '')
    pagina_actual = request.args.get('page', 1, type=int)
    elementos_por_pagina = 4

    query = db.session.query(Producto)
    
    id_pattern = r"^[TJPAS]\d{4}$"

    if nombre:
        if re.match(id_pattern, nombre):
            # Si coincide con el patrón del ID, filtra por `id`
            query = query.filter(Producto.id == nombre)
        else:
            # Si no, filtra por `nombre`
            query = query.filter(
                            or_(
                                Producto.nombre.ilike(f"%{nombre}%"),
                                Producto.color.ilike(f"%{nombre}%"),
                                Producto.id.ilike(f"%{nombre}%") # Ejemplo de otra columna
                            )
                        )
    if categoria:
        if categoria == "best":
            query = query.filter(Producto.salidas > 5).order_by(desc(Producto.salidas))
        else:
            query = query.filter(Producto.categoria == categoria)

    # Ordenar alfabéticamente por ID
    query = query.order_by(Producto.id)

    # Aplicar paginación a la consulta
    productos = query.paginate(page=pagina_actual, per_page=elementos_por_pagina)
        
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

    # Incluir información de paginación en la respuesta
    return jsonify({
        "status": username,
        "productos": productos_data,
        "consulta": consulta,
        "page": productos.page,
        "pages": productos.pages,
        "has_next": productos.has_next,
        "has_prev": productos.has_prev,
        "next_num": productos.next_num,
        "prev_num": productos.prev_num
    })
    
