from graphene import Schema, ObjectType, List, Field, Int
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models import Patate


class PatateType(SQLAlchemyObjectType):
    class Meta:
        model = Patate

class Query(ObjectType):
    patates = List(PatateType)
    patate = Field(PatateType, id=Int(required=True))

    def resolve_patates(self, info):
        return Patate.query.all()

    def resolve_patate(self, info, id):
        return Patate.query.get(id)

schema = Schema(query=Query)
