from flask import Flask
from config.settings import Config
from flask_socketio import SocketIO
from app.routes import setup_routes

socketio = SocketIO(cors_allowed_origins='*', manage_session=True)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio.init_app(app)

    from app.routes import setup_routes
    setup_routes(app)

    return app, socketio
