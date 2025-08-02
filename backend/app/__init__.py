from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask("terrahacks-backend")

app.config.from_object("app.configuration.DevelopmentConfig")

db = SQLAlchemy(app)

lm = LoginManager()
lm.setup_app(app)
lm.login_view = "login"
