from models.Usuario import crear_usuario, obtener_usuario_por_id, editar_usuario, obtener_password
from pyFunctions.cryptoUtils import hasheo, generate_key_pair,  verifvalidbs64, generate_rsa_pair, verify_private_key
import os
import tempfile

def nuevo_empleado(name, lstname, email, number, id, password):
    real_password = hasheo(password)
    if id != 'admin':
        priv_key, pub_key = generate_key_pair() #ECDSA
    else:
        priv_key, pub_key = generate_rsa_pair() #PARA EL ADMIN GENERA CLAVES DE RSA
    if(crear_usuario(id, name, lstname, email, number, real_password, pub_key)):
        #Guardamos la priv_key
        private_key_path = store_privkey(id,priv_key)
        return private_key_path, priv_key
    return None, None

def store_privkey(username, priv_key):
    temp_dir = tempfile.gettempdir()
    private_key_path = os.path.join(temp_dir, f"{username}_private_key.pem")
    with open(private_key_path, 'w') as f:
        f.write(priv_key)
    return private_key_path


def verif_clave(priv_key, pub_key):
    if verifvalidbs64(priv_key): #si está en codifbase64
        if verify_private_key(pub_key, priv_key):
            return True 
        else:
            return False
    else:
        return False


def auth(id, password, data_file):
    usuario = obtener_usuario_por_id(id)
    verif = True
    if usuario:
        real_password = hasheo(password)

        if data_file != None:
            verif = verif_clave(data_file, usuario.publickey)

        if real_password == usuario.password and verif:
            return True #todo es corecto
        else:
            return False #contraseña o documento incorrecto
        
    else:
        return False
    
def autoriza_edit(id, password, nombre, apellido,email,phone,newpassword,userid):
    if userid == 'admin':
        autentica = obtener_password(userid) #si el cambio lo solicita el admin, se usa la contraseña del admin
        usuario = obtener_usuario_por_id(id)
    else:
        usuario = obtener_usuario_por_id(id) #sino se declara como autentica (valor para verificar) la del usuario que lo solicita
        autentica = usuario.password
    if usuario:
        real_password = hasheo(password) #la contraseña esta hasheada en la db, por lo que se aplica a la contraseña recibida del form
        if real_password == autentica: #si la confirmación es correcta
            if newpassword != None: #si se detecta un cambio de contraseña
                newpassword = hasheo(newpassword)
                return editar_usuario(usuario,nombre,apellido,email,phone,newpassword, None)
            else:
                return editar_usuario(usuario,nombre,apellido,email,phone,newpassword, None)
        else:
            return False
    else:
        return False
    