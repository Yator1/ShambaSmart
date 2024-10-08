from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
DB_NAME = "crop_production.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.instance_path, DB_NAME)}'

    app.config['UPLOAD_FOLDER'] = path.join(app.instance_path, 'uploads') # uploads will be in the instance folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Set up logging
    if not app.debug:
        # Configure log file
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)    

    db.init_app(app)
    migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Farmer

    # with app.app_context():
    #     create_database(app)

    # user authentication and session management
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Farmer.query.get(int(id))
    return app

# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all()
#         print('database created')
