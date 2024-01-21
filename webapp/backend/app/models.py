from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from graphene_sqlalchemy import SQLAlchemyObjectType

from app import db


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
    phone = db.Column(db.String())

    locations: Mapped[List["PatateLocation"]] = db.relationship('PatateLocation')
    pokemons: Mapped[List["Pokemon"]] = db.relationship('Pokemon')
    spirit_animal: Mapped["SpiritAnimal"] = db.relationship('SpiritAnimal')


    def __init__(self, first_name, last_name, birth_date, birth_country,
                 birth_city, gender, email, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.birth_country = birth_country
        self.birth_city = birth_city
        self.gender = gender
        self.email = email
        self.phone = phone

    def __repr__(self):
        return f"<id {self.id}>"


class PatateLocation(db.Model):
    __tablename__ = "patate_locations"

    id = db.Column(db.Integer, primary_key=True)
    patate_id = mapped_column(ForeignKey("patates.id"))
    country = db.Column(db.String())
    city = db.Column(db.String())
    address = db.Column(db.String())
    post_code = db.Column(db.String())
    from_timestamp = db.Column(db.Date())
    to_timestamp = db.Column(db.Date())

    def __init__(self, patate_id, from_timestamp, to_timestamp,
                 city, country, address, post_code):
        self.patate_id = patate_id
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.city = city
        self.country = country
        self.address = address
        self.post_code = post_code

    def __repr__(self):
        return f"<id {self.id}>"


class Pokemon(db.Model):
    __tablename__ = "pokemon"

    id = db.Column(db.Integer, primary_key=True)
    patate_id = mapped_column(ForeignKey("patates.id"))
    name = db.Column(db.String())
    description = db.Column(db.String())
    l1_image_path = db.Column(db.String())
    l2_image_path = db.Column(db.String())
    l3_image_path = db.Column(db.String())

    def __init__(self, patate_id, name, l1_image_description,
                 l2_image_description, l3_image_description,
                 l1_image_path, l2_image_path, l3_image_path):
        self.patate_id = patate_id
        self.name = name
        self.l1_image_description = l1_image_description
        self.l2_image_description = l2_image_description
        self.l3_image_description = l3_image_description
        self.l1_image_path = l1_image_path
        self.l2_image_path = l2_image_path
        self.l3_image_path = l3_image_path

    def __repr__(self):
        return f"<id {self.id}>"


class SpiritAnimal(db.Model):
    __tablename__ = "spirit_animal"

    id = db.Column(db.Integer, primary_key=True)
    patate_id = mapped_column(ForeignKey("patates.id"))
    name = db.Column(db.String())
    description = db.Column(db.String())
    image_path = db.Column(db.String())

    def __init__(self, patate_id, name, description, image_path):
        self.patate_id = patate_id
        self.name = name
        self.description = description
        self.image_path = image_path

    def __repr__(self):
        return f"<id {self.id}>"
