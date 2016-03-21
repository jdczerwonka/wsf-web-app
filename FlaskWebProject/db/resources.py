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

polynomial = numpy.polynomial.polynomial.Polynomial

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
parser.add_argument('model_g_adj', action='append')
parser.add_argument('model_fc_adj', action='append')

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

        w2fDeath1 = [0]
        w2fDeath2 = [-0.2500, 23.9464, -4.30357143]
        w2fDeath3 = [11]
        w2fDeath4 = [-526.6290 + 11, 66.8357, -2.03571429]
        w2fDeath5 = [-725.9390 + 11, 64.3674, -1.35984848]
        w2fDeath6 = [0]

        w2fDeath_br = [0, 5, 13.1, 19.1, 27]

        finModel = [0, 210.431209, -65.244076, 9.294793, -0.678313, 0.024900, -0.000365]
        awgModel = [0.43503557, 2.16250341, -0.09743488, 0.00122924]
        awfiModel = [0.90582088, 1.59691733, 0.24820408, -0.01655183, 0.00028117]
        awfcModel = [1.1, 0.10728206]
        awgAdjust = [273, 0, 24.5]
        awfcAdjust = [2.65, 24.5]

        feed_cost_br = [2.62141065, 4.12473822, 
				        6.29822741, 8.85710311, 11.78041278, 14.48593525,
				        17.1341315, 17.63894897, 18.8702043, 20.1224158]

        feed_cost_br_wt = [ 20., 30.,
					        50., 80., 120., 160.,
            		        200., 225., 245., 265.]

        priceCutoff = [	0.29438071, 0.18980649, 0.11205248,
				        0.09077630, 0.08552250, 0.07965624, 0.07812813,
				        0.07665118, 0.07570529, 0.09360718, 0.09719425]

        args['feed_pr'] = [float(x) for x in args['feed_pr']]
        args['feed_wt'] = [float(x) for x in args['feed_wt']]

        args['model_g_adj'] = [float(x) for x in args['model_g_adj']]
        args['model_fc_adj'] = [float(x) for x in args['model_fc_adj']]

        awg_poly = [polynomial(awgModel), polynomial(awgModel) * (1 + (0.089 * 1)), polynomial(awgModel) * (1 + (0.089 * 0.8))]
        awg_br = [21., 23.]
        awg_br_wt = [245., 265.]
        awgModel = PiecePolynomial(awg_poly, awg_br, awg_br_wt)

        awfc_poly = [polynomial(awfcModel), polynomial(awfcModel) * (1 - (0.142 * 1)), polynomial(awfcModel) * (1 - (0.142 * 0.8))]
        awfc_br = [21., 23.]
        awfcModel = PiecePolynomial(awfc_poly, awfc_br)

        feed_cost_poly = []
        for cost in args['feed_pr']:
            feed_cost_poly.append(polynomial([cost]))

        feedCostModel = PiecePolynomial(feed_cost_poly, feed_cost_br, args['feed_wt'])

        death_poly = [polynomial(w2fDeath1), polynomial(w2fDeath2), polynomial(w2fDeath3), polynomial(w2fDeath4), polynomial(w2fDeath5), polynomial(w2fDeath6)]
        death_br = w2fDeath_br

        deathModel = PiecePolynomial(death_poly, death_br)

        rentModel = PiecePolynomial([polynomial(0), polynomial(2030)], [0.])

        sm = SalesModel(CarcassAvg = 218, CarcassStdDev = args['carcass_std_dev'], LeanAvg =args['lean_avg'], LeanStdDev = args['lean_std_dev'], YieldAvg = args['yield_avg'], BasePrice = args['base_price'])
        gm = PigGrowthModel(awgModel, awfcModel, feedCostModel, args['model_g_adj'], args['model_fc_adj'], StartWeight = args['start_wt'])
        bm = BarnModel(deathModel, rentModel, gm, sm, StartNum = args['start_num'], DeathLossPer = args['death_per'], DiscountLossPer = args['discount_per'], DiscountPricePer = 50, AvgWeeksInBarn = args['weeks'])

        if args['curve'].upper() == 'OPT_PRICE':
            x = numpy.arange(250, 301, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_rev_curve(x).tolist()})
        elif args['curve'].upper() == 'OPT_PRICE_RANGE':
            x = numpy.arange(50, 111, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_opt_price_curve(x)})
