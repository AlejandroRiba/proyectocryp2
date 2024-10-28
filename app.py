from flask import Flask, render_template, session, request, redirect, send_file, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from models.Producto import obtener_productos, crear_producto_con_variantes, obtener_producto_por_id, delete_product, editar_producto_con_variantes
from models.Usuario import obtener_usuario_por_id
from models.Cliente import crear_cliente_con_tarjeta
from models.Transaccion import crear_transaccion_con_detalles
from models.Tarjeta import obtener_tarjeta_por_numero
from datetime import datetime
import pyFunctions.mainfunc as mainfunc
import os
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
        cargo = session['cargo']
    else:
        username = None
        cargo = None
    return render_template("index.html", status=username, cargo=cargo)

# Ruta para crear iniciar sesión (renderiza un formulario)
@app.route('/login_route', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        data = request.form
        access, cargo = mainfunc.auth(data['id'], data['password'])
        if access:
            session['username'] = data['id']
            session['cargo'] = cargo
            return redirect('/')  # Redirigir a la página principal después de iniciar sesión
        else:
            flash("Incorrect username or password", "error")
            return redirect('/login_route')
    else:
        if 'username' in session: #si ya hay una sesión iniciada, entonces manda a al pantalla de inicio
            return redirect('/')
        else:
            return render_template('login.html')
    

# Ruta para crear iniciar sesión (renderiza un formulario)
@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        data = request.form
        private_key_path = mainfunc.nuevo_empleado(data['name'],data['lstname'],data['email'],data['number'],data['id'],data['password'])
        if private_key_path != None:
            session['username'] = data['id']
            session['cargo'] = 'employee'
            session['private_key_path'] = private_key_path
            return redirect(url_for('mostrar_descarga'))  # Redirigir a la página principal después de crear el usuario
        else:
            #no se pudo crear el usuario
            return redirect('/')
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
        if ('username' in session) and (session['cargo'] == 'admin'): #si ya hay una sesión iniciada y es el admin
            cargo = session['cargo']
            return render_template('consulta_empleado.html', cargo=cargo)
        else:
            return redirect('/')
        
#Ruta para renderizar la plantilla de editar empleado
@app.route('/edit_user/<string:id>', methods=['GET'])
def edit_user(id):
    if 'username' in session:
        usuario = obtener_usuario_por_id(id)
        username = session['username']
        cargo = session['cargo']
        return render_template('editar_usuario.html', usuario=usuario, status=username, cargo=cargo) #se mantienen los datos de status y cargo pq puede editar el dueño
    return redirect('/consulta_productos')

#Ruta para editar los datos de un empleado 
@app.route('/editar_empleado', methods=['POST'])
def editar_empleado():
    if 'username' in session:
        id = request.form['id']
        name = request.form['name']
        lastname = request.form['lstname']
        number = request.form['number']
        email = request.form['email']
        password = request.form['password']
        if 'newpassword' in request.form:
            newpassword = request.form['newpassword']
            newpassword2 = request.form['newpassword2']
            print(newpassword, newpassword2)
            print('hola, detecto el cambio de contraseña')
        print(id,name,lastname,number,email,password)
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
            cargo = session['cargo']
            return render_template('consulta_informes.html', status=username, cargo=cargo)
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
            cargo = session['cargo']
            productos = obtener_productos()
            return render_template('consulta_productos.html', status=username, cargo=cargo, productos=productos)
        else:
            return redirect('/login_route')
        
# Ruta para crear producto
@app.route('/crear_producto', methods=['GET', 'POST'])
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
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('crear_producto.html', status=username, cargo=cargo)
        else:
            return redirect('/login_route')
        
#Ruta para renderizar la plantilla de editar
@app.route('/editar_producto/<string:id>', methods=['GET'])
def editar_producto(id):
    if 'username' in session:
        producto = obtener_producto_por_id(id)
        username = session['username']
        cargo = session['cargo']
        return render_template('editar_producto.html', producto=producto, status=username, cargo=cargo)
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
    if request.method == 'POST':
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
            cargo = session['cargo']
            return render_template('registra_cliente.html', status=username, cargo=cargo)
        else:
            return redirect('/')
        
# Ruta para consultar clientes
@app.route('/consulta_clientes', methods=['GET', 'POST'])
def consulta_clientes():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('consulta_clientes.html', status=username, cargo=cargo)
        else:
            return redirect('/')
        
# Ruta para crear/registrar un ventas
@app.route('/registra_venta', methods=['GET', 'POST'])
def registra_venta():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            productos = obtener_productos()
            return render_template('registra_venta.html', status=username, cargo=cargo, productos=productos)
        else:
            return redirect('/')
        
@app.route('/procesar_venta', methods=['GET', 'POST'])
def procesar_venta():
    if request.method == 'POST':
        data = request.form

        productos = json.loads(data.get('seleccionados'))
        nombre = data['nombre']
        apellido = data['apellido']
        numero = data['numero']
        card = data['card']
        username = session['username']
        monto = 0
        
        tarjeta = obtener_tarjeta_por_numero(card)
        print(tarjeta.id)

        for producto in productos:
            item = obtener_producto_por_id(producto["id"])
            monto += item.precio * int(producto['cantidad'])

        crear_cliente_con_tarjeta(nombre=nombre, apellido=apellido, telefono=numero, numero_tarjeta=card)
        crear_transaccion_con_detalles(empleado_id=username, fecha=datetime.now(), monto=monto, productos=productos, tarjeta_id=tarjeta.id)

        return redirect('/')
    else:
        return redirect('/')

        
# Ruta para consultar ventas
@app.route('/consulta_venta', methods=['GET', 'POST'])
def consulta_venta():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('consulta_venta.html', status=username, cargo=cargo)
        else:
            return redirect('/')
        
# Ruta para manejar el inicio de sesión del admin
@app.route('/datos_admin', methods=['GET', 'POST'])
def datos_admin():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            return redirect('/') 
        else:
            return render_template('datos_admin.html')
        
# Ruta para generar un informe
@app.route('/generar_informe', methods=['GET', 'POST'])
def generar_informe():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('generar_informe.html', status=username, cargo=cargo)
        else:
            return redirect('/')
        
# Ruta para desplegar opciones sobre clientes
@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST':
        #manejar la lógica
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('opciones_clientes.html', status=username, cargo=cargo)
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
            cargo = session['cargo']
            return render_template('opciones_ventas.html', status=username, cargo=cargo)
        else:
            return redirect('/login_route')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('cargo', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)