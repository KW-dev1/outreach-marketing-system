import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config, INSTANCE_DIR

db = SQLAlchemy()


def create_app(config_class=Config):
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    from app.routes import api_bp

    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app
