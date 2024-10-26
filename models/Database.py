from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def getDatabase():
    return db