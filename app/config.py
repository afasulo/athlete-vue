import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://adam:hope@localhost:5432/athlete_vue'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # HitTrax source database configuration
    HITTRAX_DB = {
        'server': os.environ.get('HITTRAX_SERVER'),
        'port': int(os.environ.get('HITTRAX_PORT', 1433)),
        'database': os.environ.get('HITTRAX_DATABASE'),
        'user': os.environ.get('HITTRAX_USER'),
        'password': os.environ.get('HITTRAX_PASSWORD'),
    }
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'