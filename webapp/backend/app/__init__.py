import os
from logging.config import dictConfig
from pathlib import Path

from yaml import load, CLoader as Loader
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basepath = Path(__file__).parent.parent

with open(basepath / "config.yml") as f:
    data = {k: v for v in load(f, Loader=Loader)["postgres"] for k, v in v.items()}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = data['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
