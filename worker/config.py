# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user1:piero@db/DAEAlab08'  # Cambia estos valores
    SQLALCHEMY_TRACK_MODIFICATIONS = False