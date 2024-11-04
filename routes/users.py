from flask import Blueprint, jsonify, redirect, render_template, request, session

from models.Usuario import obtener_empleados, obtener_usuario_por_id
from pyFunctions import mainfunc


users_blueprint = Blueprint('users', __name__)

# Ruta para consultar empleados
@users_blueprint.route('/consulta_empleado', methods=['GET'])
def consulta_empleado():
    if (session['username'] == 'admin'): #si ya hay una sesión iniciada y es el admin
        empleados = obtener_empleados()
        username=session['username']
        return render_template('consulta_empleado.html', status=username, empleados=empleados)
    else:
        return redirect('/')
        
#Ruta para renderizar la plantilla de editar empleado
@users_blueprint.route('/edit_user/<string:id>', methods=['GET'])
def edit_user(id):
    usuario = obtener_usuario_por_id(id)
    username = session['username']
    if usuario.id == username:
        solicitud = 'personal'
    else:
        solicitud = 'ext'
    return render_template('editar_usuario.html', usuario=usuario, status=username, solicitud=solicitud) #se mantienen los datos de status y cargo pq puede editar el dueño

#Ruta para editar los datos de un empleado 
@users_blueprint.route('/editar_empleado', methods=['POST'])
def editar_empleado():
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
        if newpassword == 'admin':
            return jsonify({"success": False, "message": "The password cannot be <<admin>>.", "destino": None}), 400
        
    if mainfunc.autoriza_edit(id,password,nombre,apellido,email,number,newpassword,userid):
        return jsonify({"success": True, "message": None, "destino": '/'}), 400
    else:
        return jsonify({"success": False, "message": "Incorrect password.", "destino": None}), 400
