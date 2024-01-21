from graphene import Schema, ObjectType, List, Field, Int
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Patate, PatateLocation, SpiritAnimal, Pokemon


class PatateType(SQLAlchemyObjectType):
    class Meta:
        model = Patate


class PatateLocationType(SQLAlchemyObjectType):
    class Meta:
        model = PatateLocation


class PokemonType(SQLAlchemyObjectType):
    class Meta:
        model = Pokemon


class SpiritAnimalType(SQLAlchemyObjectType):
    class Meta:
        model = SpiritAnimal


class Query(ObjectType):
    patates = List(PatateType)
    patate = Field(PatateType, id=Int(required=True))

    def resolve_patates(self, info):
        return Patate.query.all()

    def resolve_patate(self, info, id):
        return Patate.query.get(id)

schema = Schema(query=Query)
