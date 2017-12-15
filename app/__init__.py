import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CsrfProtect
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
basedir = os.path.abspath(os.path.dirname(__file__))

# local imports
from config import config

# db variable initialization
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
csrf = CsrfProtect()

photos = UploadSet('photos', IMAGES)

def create_app(config_name):
    config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_catalog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = None

    csrf.init_app(app)

    app.config['UPLOADED_PHOTOS_DEST'] = 'app/static/img'
    configure_uploads(app, photos)

    bootstrap.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"

    from app import models

    from .user import user as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app