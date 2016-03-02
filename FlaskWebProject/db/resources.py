from flask_restful import Resource, reqparse, inputs
from flask import jsonify
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from FlaskWebProject.db.models import *
from FlaskWebProject.db.schemas import *

import datetime

SERVER = "wsf-db-server.database.windows.net"
USERNAME = "jdczerwonka@wsf-db-server"
PASSWORD = "U2,6d2s5"
DATABASE = "DietIngredientDB"

DB_URI = 'mssql+pyodbc://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?driver=SQL+Server+Native+Client+11.0'

parser = reqparse.RequestParser()
parser.add_argument('start_date', type=inputs.date)
parser.add_argument('end_date', type=inputs.date)

def CreateSession():
        engine = create_engine(DB_URI)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

class IngredientsApi(Resource):
    def get(self, IngrStr = 'ALL'):
        session = CreateSession()
        args = parser.parse_args()

        a_query = session.query(Ingredients.ingredient, func.sum(Ingredients.quantity).label('quantity'), func.sum(Ingredients.cost).label('cost'))

        if args['start_date'] is not None and args['end_date'] is not None:
            pass
        else:
            if args['start_date'] is None:
                args['start_date'] = datetime.date(2014,9,1)

            if args['end_date'] is None:
                args['end_date'] = datetime.date.today()

            a_query = a_query.join(Diets).filter(Diets.delivery_date.between(args['start_date'], args['end_date']))

        a_query = a_query.group_by(Ingredients.ingredient)

        if IngrStr.upper() == 'ALL':
            ingredients = a_query.order_by(Ingredients.ingredient.asc()).all()
        else:
            ingredients = a_query.filter(Ingredients.ingredient == IngrStr).all()
            
        schema = IngredientsSchema(many=True)
        result = schema.dump(ingredients)
        return jsonify({'ingredients' : result.data})

class GroupsApi(Resource):
    def get(self, GroupStr = 'ALL'):
        session = CreateSession()

        if GroupStr.upper() == 'ALL':
            groups = session.query(Groups).order_by(Groups.group_num.asc()).all()
        else:
            groups = session.query(Groups).filter(Groups.group_num == GroupStr).all()

        schema = GroupsSchema(many=True)
        result = schema.dump(groups)
        return jsonify({'groups' : result.data})
