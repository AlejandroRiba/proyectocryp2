from dotenv import load_dotenv
import os
import secrets
from flask import Flask

from models.Database import getDatabase

load_dotenv()

app = Flask(__name__, template_folder="templates")

# Obtener la clave secreta desde las variables de entorno
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
# La clave secreta es obligatoria para mantener seguras las sesiones.

# Configura el directorio donde se guardarán las imágenes de los productos
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/images/products')
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de la base de datos MySQL desde las variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = getDatabase()

# Inicializar la base de datos
db.init_app(app)

# Crea la carpeta si no existe
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

def getApp():
    return app
