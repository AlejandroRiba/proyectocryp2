import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils
import base64

def generate_key_pair():
    # Generar clave privada
    private_key = ec.generate_private_key(ec.SECP256R1()) #curva P-256 D 2.3 en el standard

    # Serializar la clave privada a base64
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_key_base64 = base64.b64encode(private_bytes).decode('utf-8')

    # Obtener la clave pública
    public_key = private_key.public_key()

    # Serializar la clave pública a base64
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_key_base64 = base64.b64encode(public_bytes).decode('utf-8')

    return private_key_base64, public_key_base64

def hasheo(mensaje):
    # Codifica el mensaje en bytes
    mensaje_bytes = mensaje.encode('utf-8')
    # Calcula el hash SHA-256
    hash_bytes = hashlib.sha256(mensaje_bytes).digest()
    # Codifica el hash en base64
    hash_base64 = base64.b64encode(hash_bytes)
    return hash_base64.decode('utf-8')  # Devuelve como cadena de texto