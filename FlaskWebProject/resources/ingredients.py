from FlaskWebProject.db.tables import Base, Diets, DietIngredients
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import jsonify

SERVER = "wsf-db-server.database.windows.net"
USERNAME = "jdczerwonka@wsf-db-server"
PASSWORD = "U2,6d2s5"
DATABASE = "DietIngredientDB"

DB_URI = 'mssql+pymssql://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?charset=utf8'
DB_URI_pyodbc = 'mssql+pyodbc://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?driver=SQL+Server+Native+Client+11.0'

class DietIngredientsApi(Resource):
    def get(self):
        engine = create_engine(DB_URI_pyodbc)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        ingredients = session.query(DietIngredients).filter_by(ingredient = 'Corn').first()
        return jsonify(ingredients.serialize)