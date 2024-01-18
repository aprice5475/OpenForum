# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_mail import Mail

# stdlib
from datetime import datetime
import os


db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

from .users.routes import users
from .forum.routes import forum


def custom_404(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    mail = Mail(app)

    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(forum)
    app.register_error_handler(404, custom_404)

    login_manager.login_view = "users.login"

    return app
