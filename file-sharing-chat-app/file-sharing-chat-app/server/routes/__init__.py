from flask import Blueprint

# Initialize the routes blueprint
routes_bp = Blueprint('routes', __name__)

# Import the route modules to register their routes
from .auth import *
from .file import *
from .chat import *