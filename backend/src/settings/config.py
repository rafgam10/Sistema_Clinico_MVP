import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_APP=os.getenv('FLASK_APP')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FIREBIRD_HOST = os.getenv('FIREBIRD_HOST')
    FIREBIRD_PORT = int(os.getenv('FIREBIRD_PORT', 3050))
    FIREBIRD_DATABASE = os.getenv('FIREBIRD_DATABASE')
    FIREBIRD_USER = os.getenv('FIREBIRD_USER')
    FIREBIRD_PASSWORD = os.getenv('FIREBIRD_PASSWORD')