import os
from flask import Blueprint, jsonify, make_response, redirect, render_template, request, send_file, session
from models.Usuario import confirma_existencia_admin
from pyFunctions import mainfunc

login_blueprint = Blueprint('login', __name__)

# Ruta para crear iniciar sesión (renderiza un formulario)
@login_blueprint.route('/login_route', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        data = request.form
        
        if confirma_existencia_admin(): ##si el admin ya se registro
            if 'file' not in request.files:
                return jsonify({"success": False, "message": "Try again. Admin already exists.", "destino": "/"}), 400
            
            file = request.files['file']
            data_file = file.read()
            access = mainfunc.auth(data['id'], data['password'],data_file)
            
            if not access:
                return jsonify({"success": False, "message": "Incorrect username, password or key file.", "destino": "/"}), 400
            
            session['private_key'] = data_file #Se lee en bytes y no se guarda
            session['username'] = data['id']
            return jsonify({"success": True, "message": "Welcome.", "destino": "/"}), 200  # Redirigir a la página principal después de iniciar sesión
                
        elif (data['id'] == 'admin' and data['password'] == 'admin'): ##el admin no se ha registrado
            ### AVISOOOOOOOOOO 
            ### AVISOOOOOOOOOO la validación del password = admin sería mejor cambiarla a una contraseña de un solo uso no tan obvia
            session['temporal'] = 'admin'
            return jsonify({"success": True, "message": "Welcome.", "destino": "/datos_admin"}), 200
        else:
            return jsonify({"success": False, "message": "Try again later. Admin does not exists.", "destino": None}), 400
    else:
        if 'username' in session: #si ya hay una sesión iniciada, entonces manda a al pantalla de inicio
            return redirect('/')
        return render_template('login.html')

# Ruta para cerrar sesión
@login_blueprint.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('private_key', None)
    return redirect('/')

#Ruta para manejar el registro del admin
@login_blueprint.route('/datos_admin', methods=['GET','POST'])
def datos_admin():
    if request.method == 'POST':
        data = request.form

        if data['password'] == 'admin': #Si el usuario ingresa la misma contraseña (contraseña = admin)
            return jsonify({"success": False, "message": "The password cannot be <<admin>>.", "destino": None}), 400
        
        private_key_path, private_key = mainfunc.nuevo_empleado(data['name'],data['lstname'],data['email'],data['number'],data['id'],data['password'])
        
        if private_key_path == None: # Si no se pudo crear el usuario
            return jsonify({"success": False, "message": "Something wet wrong.", "destino": None}), 400

        session['username'] = data['id']
        session['private_key_path'] = private_key_path
        session['private_key'] = private_key
        session.pop('temporal', None)
        return jsonify({"success": True, "message": "Welcome.", "destino": '/mostrar_descarga'}), 200
                  

    else:
        if 'temporal' in session:
            tmp = session['temporal']
            return render_template('datos_admin.html', status=tmp)
        return redirect('/')     

# Ruta para crear iniciar sesión (renderiza un formulario)
@login_blueprint.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        if not confirma_existencia_admin(): #Si el administrador no se ha registrado
            return jsonify({"success": False, "message": "The admin has not registered yet. Please try again later.", "destino": None}), 400
        
        data = request.form
        private_key_path, private_key = mainfunc.nuevo_empleado(data['name'],data['lstname'],data['email'],data['number'],data['id'],data['password'])
        
        if private_key_path == None: # Si el usuario ya existe o no se pudo crear
            return jsonify({"success": False, "message": "Error. The user may already exists; please check that your information is correct.", "destino": None}), 400            

        session['username'] = data['id']
        session['private_key_path'] = private_key_path
        session['private_key'] = private_key
        return jsonify({"success": True, "message": "Welcome.", "destino": '/mostrar_descarga'}), 200
    
    else:
        if 'username' in session: #si ya hay una sesión iniciada, entonces manda a al pantalla de inicio
            return redirect('/')
        return render_template('crear_usuario.html')

#Ruta para mostrar la página de descarga
@login_blueprint.route('/mostrar_descarga', methods=['GET'])
def mostrar_descarga():
    if 'private_key_path' not in session:
        return redirect('/')
    response = make_response(render_template('descargar_key.html')) #ENCABEZADOS PARA NO GUARDAR LA PÁGINA EN CACHE
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragme'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

#Ruta para permitir la descarga del archivo
@login_blueprint.route('/descargar_clave', methods=['GET'])
def descargar_clave():
    if 'private_key_path' not in session:
        return redirect('/')
    private_key_path = session['private_key_path']
    username = session['username']
    return send_file(private_key_path, as_attachment=True, download_name=f'{username}_private_key.pem')

#Ruta para confirmar que el archivo ya se descargo
@login_blueprint.route('/confirmar_descarga', methods=['POST'])
def confirmar_descarga():
    if 'private_key_path' in session:
        os.remove(session['private_key_path'])
        session.pop('private_key_path', None)
    return redirect('/')
