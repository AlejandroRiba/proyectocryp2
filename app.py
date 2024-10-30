from flask import Flask, render_template, session, request, redirect, send_file, url_for, make_response, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from models.Producto import modificar_salidas_producto, modificar_stock_variante, obtener_productos, crear_producto_con_variantes, obtener_producto_por_id, delete_product, editar_producto_con_variantes, obtener_salidas_producto, obtener_stock_variante, obtener_variante_por_id_y_talla, obtener_variantes_por_producto_id
from models.Usuario import obtener_usuario_por_id, confirma_existencia_admin, obtener_empleados
from models.Cliente import crear_cliente_con_tarjeta, obtener_cliente_por_tel
from models.Transaccion import crear_transaccion_con_detalles
from models.Tarjeta import obtener_tarjeta_por_numero
from datetime import datetime
import pyFunctions.mainfunc as mainfunc
import os
from pyFunctions.reportepdf import generar_informe_ventas_mensual
import secrets
import tempfile
import json

app = Flask(__name__, template_folder="templates")

# Generar una clave secreta aleatoria cada vez que la app se inicializa
app.secret_key = secrets.token_hex(16)  # Genera una clave de 32 caracteres hexadecimales
#La clave secreta es obligatoria para mantener seguras las sesiones.

# Configura el directorio donde se guardarán las imágenes de los productos
UPLOAD_FOLDER = 'static/images/products'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/proyecto2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = getDatabase()

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    # Verificar si el usuario está logueado
    if 'username' in session:
        username = session['username']
    else:
        username = None
    return render_template("index.html", status=username)

# Ruta para crear iniciar sesión (renderiza un formulario)
@app.route('/login_route', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        data = request.form
        if confirma_existencia_admin(): ##si el admin ya se registro
            access = mainfunc.auth(data['id'], data['password'])
            if access:
                session['username'] = data['id']
                return jsonify({"success": True, "message": "Welcome.", "destino": "/"}), 200  # Redirigir a la página principal después de iniciar sesión
            elif 'file' not in request.files:
                return jsonify({"success": False, "message": "Try again. Admin already exists.", "destino": "/"}), 400
            else:
                return jsonify({"success": False, "message": "Incorrect username or password.", "destino": "/"}), 400
        elif (data['id'] == 'admin' and data['password'] == 'admin'): ##el admin no se ha registrado
            ### AVISOOOOOOOOOO 
            ### AVISOOOOOOOOOO la validación del password = admin sería mejor cambiarla a una contraseña de un solo uso no tan obvia
            session['temporal'] = 'admin'
            return jsonify({"success": True, "message": "Welcome.", "destino": "/datos_admin"}), 200
        else:
            return jsonify({"success": False, "message": "Incorrect username or password.", "destino": "/login_route"}), 400
    else:
        if 'username' in session: #si ya hay una sesión iniciada, entonces manda a al pantalla de inicio
            return redirect('/')
        else:
            return render_template('login.html')
        
#Ruta para manejar el registro del admin
@app.route('/datos_admin', methods=['GET','POST'])
def datos_admin():
    if request.method == 'POST':
        data = request.form
        if data['password'] != 'admin':
            private_key_path = mainfunc.nuevo_empleado(data['name'],data['lstname'],data['email'],data['number'],data['id'],data['password'])
            if private_key_path != None:
                session['username'] = data['id']
                session['private_key_path'] = private_key_path
                session.pop('temporal', None)
                return jsonify({"success": True, "message": "Welcome.", "destino": '/mostrar_descarga'}), 200
            else:
                #no se pudo crear el usuario
                return redirect('/')
        else:
            return jsonify({"success": False, "message": "La contraseña no puede ser admin.", "destino": None}), 400
    else:
        if 'temporal' in session:
            tmp = session['temporal']
            return render_template('datos_admin.html', status=tmp)
        else:
            return redirect('/')
 
        

# Ruta para crear iniciar sesión (renderiza un formulario)
@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        if confirma_existencia_admin(): ##si el admin ya se registro
            data = request.form
            private_key_path = mainfunc.nuevo_empleado(data['name'],data['lstname'],data['email'],data['number'],data['id'],data['password'])
            if private_key_path != None:
                session['username'] = data['id']
                session['private_key_path'] = private_key_path
                return jsonify({"success": True, "message": "Welcome.", "destino": '/mostrar_descarga'}), 200
            else:
                return jsonify({"success": False, "message": "Error. The user may already exists; please check that your information is correct.", "destino": None}), 400
        else:
            return jsonify({"success": False, "message": "The admin has not registered yet. Please try again later.", "destino": None}), 400
    else:
        if 'username' in session: #si ya hay una sesión iniciada, entonces manda a al pantalla de inicio
            return redirect('/')
        else:
            return render_template('crear_usuario.html')

#Ruta para mostrar la página de descarga
@app.route('/mostrar_descarga', methods=['GET'])
def mostrar_descarga():
    if 'private_key_path' not in session:
        return redirect('/')
    response = make_response(render_template('descargar_key.html')) #ENCABEZADOS PARA NO GUARDAR LA PÁGINA EN CACHE
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragme'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

#Ruta para permitir la descarga del archivo
@app.route('/descargar_clave', methods=['GET'])
def descargar_clave():
    if 'private_key_path' not in session:
        return redirect('/')
    private_key_path = session['private_key_path']
    username = session['username']
    return send_file(private_key_path, as_attachment=True, download_name=f'{username}_private_key.pem')

#Ruta para confirmar que el archivo ya se descargo
@app.route('/confirmar_descarga', methods=['POST'])
def confirmar_descarga():
    if 'private_key_path' in session:
        os.remove(session['private_key_path'])
        session.pop('private_key_path', None)
    return redirect('/')

# Ruta para consultar empleados
@app.route('/consulta_empleado', methods=['GET', 'POST'])
def consulta_empleado():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session) and (session['username'] == 'admin'): #si ya hay una sesión iniciada y es el admin
            empleados = obtener_empleados()
            username=session['username']
            return render_template('consulta_empleado.html', status=username, empleados=empleados)
        else:
            return redirect('/')
        
#Ruta para renderizar la plantilla de editar empleado
@app.route('/edit_user/<string:id>', methods=['GET'])
def edit_user(id):
    if 'username' in session:
        usuario = obtener_usuario_por_id(id)
        username = session['username']
        if usuario.id == username:
            solicitud = 'personal'
        else:
            solicitud = 'ext'
        return render_template('editar_usuario.html', usuario=usuario, status=username, solicitud=solicitud) #se mantienen los datos de status y cargo pq puede editar el dueño
    return redirect('/consulta_productos')

#Ruta para editar los datos de un empleado 
@app.route('/editar_empleado', methods=['POST'])
def editar_empleado():
    if 'username' in session:
        id = request.form['id']
        nombre = request.form['name']
        apellido = request.form['lstname']
        number = request.form['number']
        email = request.form['email']
        password = request.form['password']
        newpassword = None
        userid = session['username']
        if 'newpassword' in request.form:
            newpassword = request.form['newpassword']
        if mainfunc.autoriza_edit(id,password,nombre,apellido,email,number,newpassword,userid):
            return redirect('/')
        else:
            flash("Usuario o contraseña incorrectos", "error")
            return redirect(f'/edit_user/{id}')
    return redirect('/')

# Ruta para consultar informes
@app.route('/consulta_informes', methods=['GET', 'POST'])
def consulta_informes():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('consulta_informes.html', status=username)
        else:
            return redirect('/')
        
# Ruta para consultar productos
@app.route('/consulta_productos', methods=['GET', 'POST'])
def consulta_productos():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            productos = obtener_productos()
            return render_template('consulta_productos.html', status=username, productos=productos)
        else:
            return redirect('/login_route')
        
# Ruta para crear producto
@app.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST' and ('username' in session):
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
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('crear_producto.html', status=username)
        else:
            return redirect('/login_route')
        
#Ruta para renderizar la plantilla de editar
@app.route('/editar_producto/<string:id>', methods=['GET'])
def editar_producto(id):
    if 'username' in session:
        producto = obtener_producto_por_id(id)
        username = session['username']
        return render_template('editar_producto.html', producto=producto, status=username)
    return redirect('/consulta_productos')

#Ruta para editar un producto 
@app.route('/editar_producto_query', methods=['POST'])
def editar_producto_query():
    if 'username' in session:
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
            print(f'Vieja ruta = {last_path}')
            print(f'Nueva ruta = {nuevo_path}')
            editar_producto_con_variantes(id,nombre,color,precio,variantes,variantes_a_eliminar, file.filename)
        else:
            editar_producto_con_variantes(id,nombre,color,precio,variantes,variantes_a_eliminar, None)
    return redirect('/consulta_productos')

#Ruta para eliminar un producto 
@app.route('/eliminar_producto/<string:id>', methods=['GET'])
def eliminar_producto(id):
    if 'username' in session:
        borrado, filename = delete_product(id)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if borrado: # Verificar si el archivo existe y eliminarlo
            if os.path.isfile(file_path):
                os.remove(file_path) #elimina la imagen si la consulta de delete se ejecuta con éxito
    return redirect('/consulta_productos')

# Ruta para crear/registrar un cliente
@app.route('/registra_cliente', methods=['GET', 'POST'])
def registra_cliente():
    if request.method == 'POST' and ('username' in session):
        data = request.form
        status, detalle = crear_cliente_con_tarjeta(data['nombre'], data['apellido'], data['numero'], data['card'])
        if status:
            return redirect('/')
        else:
            print(f"Error: {detalle}")
            #Manejar el error
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('registra_cliente.html', status=username)
        else:
            return redirect('/')
        
# Ruta para consultar clientes
@app.route('/consulta_clientes', methods=['GET', 'POST'])
def consulta_clientes():
    if request.method == 'POST' and ('username' in session):
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('consulta_clientes.html', status=username)
        else:
            return redirect('/')
        
# Ruta para crear/registrar un ventas
@app.route('/registra_venta', methods=['GET', 'POST'])
def registra_venta():
    if request.method == 'POST' and ('username' in session):
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            productos = obtener_productos()
            return render_template('registra_venta.html', status=username, productos=productos)
        else:
            return redirect('/')
        
@app.route('/procesar_venta', methods=['GET', 'POST'])
def procesar_venta():
    if request.method == 'POST' and ('username' in session):
        data = request.form

        productos = json.loads(data.get('seleccionados'))
        nombre = data['nombre']
        apellido = data['apellido']
        numero = data['numero']
        card = data['card']
        username = session['username']
        monto = 0
        
        tarjeta = obtener_tarjeta_por_numero(card)
        cliente = obtener_cliente_por_tel(numero) #asumiendo que el número de teléfono es único
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
        crear_cliente_con_tarjeta(nombre=nombre, apellido=apellido, telefono=numero, numero_tarjeta=card)
        crear_transaccion_con_detalles(empleado_id=username, fecha=datetime.now(), monto=monto, productos=productos, tarjeta_id=tarjeta.id, cliente_id=cliente.id)

        return redirect('/')
    else:
        return redirect('/')

        
# Ruta para consultar ventas
@app.route('/consulta_venta', methods=['GET', 'POST'])
def consulta_venta():
    if request.method == 'POST' and ('username' in session):
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('consulta_venta.html', status=username)
        else:
            return redirect('/')
        
        
# Ruta para generar un informe
@app.route('/generar_informe', methods=['GET', 'POST'])
def generar_informe():
    if request.method == 'POST' and ('username' in session):
        access = mainfunc.auth(session['username'], request.form['password'])
        if access:
            year = int(request.form['year'])
            month = int(request.form['month'])
            report, flash_message = generar_informe_ventas_mensual(session['username'], year, month)
            if report:
                return redirect('/consulta_informes')
            else:
                flash(flash_message, "error")
                return redirect('/generar_informe')
        else:
            flash("Incorrect password. Try again.", "error")
            return redirect('/generar_informe')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('generar_informe.html', status=username)
        else:
            return redirect('/')
        
# Ruta para desplegar opciones sobre clientes
@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST' and ('username' in session):
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('opciones_clientes.html', status=username)
        else:
            return redirect('/login_route')
        
# Ruta para desplegar opciones sobre ventas
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            return render_template('opciones_ventas.html', status=username)
        else:
            return redirect('/login_route')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)