from flask_restful import Resource, reqparse, inputs
from flask import jsonify
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from FlaskWebProject.db.models import *
from FlaskWebProject.db.schemas import *
from FlaskWebProject.classes.BarnModel import *
from datetime import date

SERVER = "wsf-db-server.database.windows.net"
USERNAME = "jdczerwonka@wsf-db-server"
PASSWORD = "U2,6d2s5"
DATABASE = "DietIngredientDB"

DB_URI = 'mssql+pyodbc://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?driver=SQL+Server+Native+Client+11.0'

parser = reqparse.RequestParser()
parser.add_argument('start_date', type=inputs.date)
parser.add_argument('end_date', type=inputs.date)
parser.add_argument('month_id', type=str)
parser.add_argument('week_id', type=str)

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

        if args['month_id'] is not None:
            a_query = a_query.join(Diets).filter(Diets.delivery_month == args['month_id'])
            print args['month_id']
        elif args['week_id'] is not None:
            a_query = a_query.join(Diets).filter(Diets.delivery_week == args['week_id'])
            print args['week_id']
        elif args['start_date'] is None and args['end_date'] is None:
            pass
        else:
            if args['start_date'] is None:
                args['start_date'] = date(2014,9,1)

            if args['end_date'] is None:
                args['end_date'] = date.today()

            a_query = a_query.join(Diets).filter(Diets.delivery_date.between(args['start_date'], args['end_date']))
        
        if IngrStr.upper() == 'ALL':
            ingredients = a_query.group_by(Ingredients.ingredient).order_by(Ingredients.ingredient.asc()).all()
        else:
            ingredients = a_query.group_by(Ingredients.ingredient).filter(Ingredients.ingredient == IngrStr).all()
            
        schema = IngredientsSchema(many=True)
        result = schema.dump(ingredients)
        return jsonify({'ingredients' : result.data})

class GroupsApi(Resource):
    def get(self, GroupInfo = None, GroupStr = 'ALL'):
        session = CreateSession()
        move_bool = False

        if GroupInfo is None:
            a_query = session.query(Groups)
            table = Groups
        elif GroupInfo.upper() == 'FEED':
            a_query = session.query(func.sum(Diets.quantity).label('quantity'), func.sum(Diets.cost).label('cost'), Diets.group_num).group_by(Diets.group_num)
            table = Diets
        elif GroupInfo.upper() == 'DEATHS':
            a_query = session.query(func.sum(Deaths.quantity).label('death_num'), func.sum(Deaths.weight).label('weight'), Deaths.group_num).group_by(Deaths.group_num)
            table = Deaths
        elif GroupInfo.upper() in ['ADJ', 'BGM', 'CON', 'DIS', 'DOT', 'GA', 'GS', 'NV', 'PWP', 'SA', 'SMS', 'SR', 'ST', 'TFP', 'WPS', 'YD']:
            a_query = session.query(func.abs(func.sum(Movements.quantity)).label('quantity'), func.abs(func.sum(Movements.weight)).label('weight'), func.abs(func.sum(Movements.cost)).label('cost'), Movements.location_id.label('group_num'))
            a_query = a_query.group_by(Movements.location_id).filter( ((Movements.location_type == 'group') | (Movements.location_type == 'sow_unit')) & (Movements.event_code == GroupInfo))
            table = Movements
            move_bool = True

        if move_bool:
            if GroupStr.upper() == 'ALL':
                groups = a_query.order_by(table.location_id.desc()).all()
            else:
                groups = a_query.filter(table.location_id == GroupStr).all()        
        else:
            if GroupStr.upper() == 'ALL':
                groups = a_query.order_by(table.group_num.desc()).all()
            else:
                groups = a_query.filter(table.group_num == GroupStr).all()

        schema = GroupsSchema(many=True)
        result = schema.dump(groups)
        return jsonify({'groups' : result.data})

class WeightOptApi(Resource):
    def get(self):
        pass
