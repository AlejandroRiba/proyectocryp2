import os
import secrets
from flask import Flask

from models.Database import getDatabase

app = Flask(__name__, template_folder="templates")

# Generar una clave secreta aleatoria cada vez que la app se inicializa
app.secret_key = secrets.token_hex(16)  # Genera una clave de 32 caracteres hexadecimales
#La clave secreta es obligatoria para mantener seguras las sesiones.

# Configura el directorio donde se guardarán las imágenes de los productos
UPLOAD_FOLDER = 'static/images/products'
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
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

def getApp():
    return app