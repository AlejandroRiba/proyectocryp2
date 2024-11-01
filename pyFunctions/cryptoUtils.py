import hashlib
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils
import base64
import secrets

def verifvalidbs64(x):
    try:
        base64.b64decode(x, validate=True)
        return True
    except Exception:
        return False
    
def hasheo(mensaje):
    # Codifica el mensaje en bytes
    mensaje_bytes = mensaje.encode('utf-8')
    # Calcula el hash SHA-256
    hash_bytes = hashlib.sha256(mensaje_bytes).digest()
    # Codifica el hash en base64
    hash_base64 = base64.b64encode(hash_bytes)
    return hash_base64.decode('utf-8')  # Devuelve como cadena de texto

def verify_private_key(public_key, private_key):
    #Decodificar las claves
    public_key_bytes = base64.b64decode(public_key)
    private_key_bytes = base64.b64decode(private_key)

    #Cargar las claves 
    public_key = serialization.load_pem_public_key(
        public_key_bytes
    )
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None,
    )
    key_prueba = private_key.public_key()
    if key_prueba == public_key:
        return True
    else:
        return False


def gen_AESkey():
    key = secrets.token_bytes(16) #llave de 128 bits
    return key
    
def generate_rsa_pair():
    # Generar clave privada
    # public exponent según el NIST debe ser un valor entre 2^16 y 2^256 para garantizar seguridad y eficacia
    private_key = rsa.generate_private_key( 
        public_exponent=65537,  # e debe ser 65537 para una buena seguridad
        key_size=2048  # Tamaño de clave en bits
    )
    public_key = private_key.public_key()

    #Serializar la clave privada a base 64
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    public_key_base64 = base64.b64encode(public_bytes).decode('utf-8')
    private_key_base64 = base64.b64encode(private_bytes).decode('utf-8')
    print(public_key_base64)
    return private_key_base64, public_key_base64

def encrypt_with_publickey(public_key, message): #FUNCIÓN PARA PROTEGER LLAVE DE AES
    #Decodificar la clave
    public_key_bytes = base64.b64decode(public_key)

    #Cargar la clave real
    public_key = serialization.load_pem_public_key(
        public_key_bytes
    )

    #Cifrar el mensaje
    ciphertext = public_key.encrypt(
        message, #Se agrega el padding ya que necesitamos bloques del mismo tamaño. 
        padding.OAEP(  #NIST SP 800-56B Rev. 2
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(ciphertext).decode('utf-8')

def decrypyt_with_privatekey(private_key, ciphertext):
    #Decodificar la clave
    private_key_bytes = base64.b64decode(private_key)

    #Cargar la clave real
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None,
    )

    # Decodificar el ciphertext de base64
    decoded_ciphertext = base64.b64decode(ciphertext)

    # Desencriptar el mensaje
    plaintext = private_key.decrypt(
        decoded_ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext.decode('utf-8')

def sign_message_rsa(private_key, message):
    print('Sign message with rsa')
    #Decodificar la clave
    private_key_bytes = base64.b64decode(private_key)

    #Cargar la clave real
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None,
    )

    #Generar firma con RSA
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    #Retornamos la firma
    return signature

def verify_signature_rsa(public_key, message, signature):
    print('Verify sign with rsa')
    #Decodificar la clave
    public_key_bytes = base64.b64decode(public_key)

    #Cargar la clave real
    public_key = serialization.load_pem_public_key(
        public_key_bytes
    )
    # Verificar la firma
    try:
        public_key.verify(
            signature, 
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True #firma verificada
    except:
        return False

def generate_key_pair(): #ECDSA
    # Generar clave privada
    private_key = ec.generate_private_key(ec.SECP256R1()) #curva P-256 D 2.3 en el standard

    # Serializar la clave privada a base64
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
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


def sign_message_ECDSA(private_key, message):
    # Leer la clave privada desde el archivo
    private_key_bytes = base64.b64decode(private_key) #decodificamos de base 64
    
    # Cargar la clave privada
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        password=None
    )
    
    # Crear la firma
    signature = private_key.sign(
        message, #ya se recibe en bytes
        ec.ECDSA(hashes.SHA256())
    )

    # Retorna la firma
    return signature

def verify_signature_ECDSA(public_key, contenido, signature):
    # Decoficar la clave pública
    public_key_bytes = base64.b64decode(public_key)
    
    # Cargar la clave pública
    public_key = serialization.load_pem_public_key(
        public_key_bytes
    )

    # Verificar la firma
    try:
        public_key.verify(
            signature,
            contenido,
            ec.ECDSA(hashes.SHA256())
        )
        return True #firma verificada
    except:
        return False
