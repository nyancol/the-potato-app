from app import app
from eralchemy2 import render_er

print(app.config["SQLALCHEMY_DATABASE_URI"])
# app.config["SQLALCHEMY_DATABASE_URI"]
url = "postgresql+psycopg2://potatoadmin:potato@localhost:5432/potato"
render_er(url, 'er_diagram.png')
