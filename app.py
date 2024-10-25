from flask import Flask, render_template, session, request, redirect, send_file, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from queries import db
import mainfunc
import os
import secrets
import tempfile

app = Flask(__name__, template_folder="templates")

# Generar una clave secreta aleatoria cada vez que la app se inicializa
app.secret_key = secrets.token_hex(16)  # Genera una clave de 32 caracteres hexadecimales
#La clave secreta es obligatoria para mantener seguras las sesiones.

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/proyecto2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        if mainfunc.auth(data['id'], data['password']):
            session['username'] = data['id']
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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)