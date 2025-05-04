from .auth import auth_routes
from .file import file_routes
from .chat import chat_routes

def register_routes(app):
    app.register_blueprint(auth_routes)
    app.register_blueprint(file_routes)
    app.register_blueprint(chat_routes)