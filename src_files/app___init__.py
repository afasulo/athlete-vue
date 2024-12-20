# app/__init__.py
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from app.config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.api import bp as api_bp
    from app.dashboard import bp as dashboard_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    @app.route('/')
    def index():
        return redirect('/dashboard/player')
    
    return app