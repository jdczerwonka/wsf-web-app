from flask_restful import Resource, reqparse, inputs
from flask import jsonify
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from FlaskWebProject.db.models import *
from FlaskWebProject.db.schemas import *
from FlaskWebProject.classes.BarnModel import *
from datetime import date
import numpy
import simplejson

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
parser.add_argument('curve', type=str, default='OPT_PRICE')
parser.add_argument('start_num', type=int, default=2500)
parser.add_argument('start_wt', type=float, default=12)
parser.add_argument('base_price', type=float, default=80)
parser.add_argument('rent', type=float, default=1940)
parser.add_argument('weeks', type=float, default=24.5)
parser.add_argument('death_per', type=float, default=4)
parser.add_argument('discount_per', type=float, default=1)
parser.add_argument('carcass_std_dev', type=float, default=18)
parser.add_argument('lean_avg', type=float, default=54)
parser.add_argument('lean_std_dev', type=float, default=2.1)
parser.add_argument('yield_avg', type=float, default=76)
parser.add_argument('feed_pr', action='append')
parser.add_argument('feed_wt', action='append')

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
        args = parser.parse_args()

        w2fModel = [0, 288.798017, -81.388061, 10.101958, -0.623565, 0.018835, -0.000222]
        finModel = [0, 210.431209, -65.244076, 9.294793, -0.678313, 0.024900, -0.000365]
        awgModel = [0.43503557, 2.16250341, -0.09743488, 0.00122924]
        awfcModel = [1.1, 0.10728206]
        awgAdjust = [273, 0, 24.4]
        awfcAdjust = [2.64, 0, 24.4]

        wtCutoff = numpy.array([12, 20, 30,
                    50, 80, 120, 160,
                    200, 225, 245, 265])

        priceCutoff = [0.29721160, 0.19111814, 0.11239397,
                        0.09492490, 0.08964955, 0.08389767, 0.08180934,
                        0.08025336, 0.07925855, 0.09876173, 0.10228566]

        priceCutoff2 = [0.34228121, 0.23497637, 0.15338756,
				        0.10120521, 0.10381095, 0.09572995, 0.08078402,
				        0.07826039, 0.07829362, 0.10029394, 0.10316896]

        priceCutoff3 = [0.29438071, 0.18980649, 0.11205248,
				        0.09077630, 0.08552250, 0.07965624, 0.07812813, 
				        0.07665118, 0.07570529, 0.09360718, 0.09719425]

        args['feed_pr'] = [float(x) for x in args['feed_pr']]
        args['feed_wt'].insert(0, args['start_wt'])
        args['feed_wt'] = [float(x) for x in args['feed_wt']]

        sm = SalesModel(CarcassAvg = 218, CarcassStdDev = args['carcass_std_dev'], LeanAvg =args['lean_avg'],
                LeanStdDev = args['lean_std_dev'], YieldAvg = args['yield_avg'], BasePrice = args['base_price'])

        gm = PigGrowthModel(awgModel, awfcModel, args['weeks'], awgAdjust, awfcAdjust, PriceCutoff = args['feed_pr'], WtCutoff = numpy.array(args['feed_wt']), StartWeight = args['start_wt'])

        bm = BarnModel(w2fModel, gm, sm, StartNum = args['start_num'], DeathLossPer = args['death_per'], DiscountLossPer = args['discount_per'], WeeklyRent = args['rent'])

        if args['curve'].upper() == 'OPT_PRICE':
            x = numpy.arange(250, 301, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_rev_curve(x).tolist()})
        elif args['curve'].upper() == 'OPT_PRICE_RANGE':
            x = numpy.arange(50, 111, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_opt_price_curve(x)})
