# app/api/__init__.py
from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes  # This import must be after bp creation