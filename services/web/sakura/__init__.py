from flask import Flask, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config.from_object("sakura.config.Config")
db = SQLAlchemy(app)

from . import routes

class User(db.Model):
    __tablename__ = "users"

