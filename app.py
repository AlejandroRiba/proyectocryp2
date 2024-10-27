from flask import Flask, render_template, session, request, redirect, send_file, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from models.Database import getDatabase
from models.Producto import obtener_productos, crear_producto_con_variantes
from models.Cliente import crear_cliente_con_tarjeta
import pyFunctions.mainfunc as mainfunc
import os
import secrets
import tempfile

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
        return redirect('/')  # Redirigir a la página principal después de crear el usuario
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

        file = request.files['image']
        variantes = []
        tallas = request.form.getlist('talla')
        stocks = request.form.getlist('stock')

        # Agrupar tallas y stocks
        for talla, stock in zip(tallas, stocks):
            variantes.append({'talla': talla, 'stock': stock})
        crear_producto_con_variantes(id, nombre, color, precio, variantes, file.filename)
        #guardar la imagen del producto
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect('/')
    else:
        if ('username' in session): #si ya hay una sesión iniciada
            username = session['username']
            cargo = session['cargo']
            return render_template('crear_producto.html', status=username, cargo=cargo)
        else:
            return redirect('/login_route')
        
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
            return render_template('registra_venta.html', status=username, cargo=cargo)
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