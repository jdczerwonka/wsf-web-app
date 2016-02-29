from flask_restful import Resource
from flask import jsonify
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from FlaskWebProject.db.tables import Base, Diets, Ingredients
from FlaskWebProject.db.schemas import IngredientsSchema

SERVER = "wsf-db-server.database.windows.net"
USERNAME = "jdczerwonka@wsf-db-server"
PASSWORD = "U2,6d2s5"
DATABASE = "DietIngredientDB"

DB_URI_pyodbc = 'mssql+pyodbc://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?driver=SQL+Server+Native+Client+11.0'

def CreateSession():
        engine = create_engine(DB_URI_pyodbc)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

class IngredientsApi(Resource):
    def get(self):
        session = CreateSession()
        ingredients = session.query(Ingredients.ingredient, func.sum(Ingredients.quantity).label('quantity'), func.sum(Ingredients.cost).label('cost')).group_by(Ingredients.ingredient).order_by(Ingredients.ingredient.asc()).all()
        schema = IngredientsSchema(many=True)
        result = schema.dump(ingredients)
        return jsonify({'ingredients' : result.data})

class IngredientApi(Resource):
    def get(self, IngrStr):
        session = CreateSession()
        ingredients = session.query(Ingredients.ingredient, func.sum(Ingredients.quantity).label('quantity'), func.sum(Ingredients.cost).label('cost')).group_by(Ingredients.ingredient).filter(Ingredients.ingredient == IngrStr).all()
        print ingredients
        schema = IngredientsSchema(many=True)
        result = schema.dump(ingredients)
        return jsonify({'ingredient' : result.data})