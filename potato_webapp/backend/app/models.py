from app import db
from graphene_sqlalchemy import SQLAlchemyObjectType


class Patate(db.Model):
    __tablename__ = 'patates'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    birth_date = db.Column(db.Date())
    birth_country = db.Column(db.String())
    birth_city = db.Column(db.String())
    gender = db.Column(db.String())
    email = db.Column(db.String())

    def __init__(self, first_name, last_name, birth_date, birth_country,
                 birth_city, gender, email):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.birth_country = birth_country
        self.birth_city = birth_city
        self.gender = gender
        self.email = email

    def __repr__(self):
        return '<id {}>'.format(self.id)
