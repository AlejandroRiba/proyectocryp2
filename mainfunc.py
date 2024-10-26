from models.Usuario import crear_usuario, obtener_usuario_por_id
from cryptoUtils import hasheo, generate_key_pair
import os
import tempfile

def nuevo_empleado(name, lstname, email, number, id, password):
    real_password = hasheo(password)
    priv_key, pub_key = generate_key_pair()
    if(crear_usuario(id, name, lstname, email, number, real_password, pub_key)):
        #Guardamos la priv_key
        private_key_path = store_privkey(id,priv_key)
        return private_key_path
    return None

def store_privkey(username, priv_key):
    temp_dir = tempfile.gettempdir()
    private_key_path = os.path.join(temp_dir, f"{username}_private_key.pem")
    with open(private_key_path, 'w') as f:
        f.write(priv_key)
    return private_key_path

def auth(id, password):
    usuario = obtener_usuario_por_id(id)
    real_password = hasheo(password)
    if real_password == usuario.password:
        return True, usuario.cargo
    else:
        return False