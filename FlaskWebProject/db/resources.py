from __future__ import division
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
import json

SERVER = "wsf-db-server.database.windows.net"
USERNAME = "jdczerwonka@wsf-db-server"
PASSWORD = "U2,6d2s5"
DATABASE = "DietIngredientDB"

DB_URI = 'mssql+pyodbc://' + USERNAME + ':' + PASSWORD + '@' + SERVER + '/' + DATABASE + '?driver=SQL+Server+Native+Client+11.0'

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
awfcAdjust = [2.65, 0, 24.5]

feed_cost_br = [2.62141065, 4.12473822, 
				6.29822741, 8.85710311, 11.78041278, 14.48593525,
				17.1341315, 17.63894897, 18.8702043, 20.1224158]

feed_cost_br_wt = [ 20., 30.,
					50., 80., 120., 160.,
            		200., 225., 245., 265.]

priceCutoff = [	0.29438071, 0.18980649, 0.11205248,
				0.09077630, 0.08552250, 0.07965624, 0.07812813,
				0.07665118, 0.07570529, 0.09360718, 0.09719425]

awg_poly = [polynomial(awgModel), polynomial(awgModel) * (1 + (0.089 * 1)), polynomial(awgModel) * (1 + (0.089 * 0.8))]
awg_br = [21., 23.]
awg_br_wt = [245., 265.]
awgModel = PiecePolynomial(awg_poly, awg_br, awg_br_wt)

awfc_poly = [polynomial(awfcModel), polynomial(awfcModel) * (1 - (0.142 * 1)), polynomial(awfcModel) * (1 - (0.142 * 0.8))]
awfc_br = [21., 23.]
awfcModel = PiecePolynomial(awfc_poly, awfc_br)

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

parser.add_argument('budget_type', type=str)

parser.add_argument('group_num', type=str)
parser.add_argument('wof_avg', type=float)
parser.add_argument('wof_tot', type=float)
parser.add_argument('start_num', type=int)
parser.add_argument('start_avg_wt', type=float)
parser.add_argument('start_avg_price_pig', type=float) #correction
parser.add_argument('market_num', type=int)
parser.add_argument('gilt_num', type=int)
parser.add_argument('discount_num', type=int)
parser.add_argument('death_num', type=int)
parser.add_argument('transport_death_num', type=int)
parser.add_argument('transfer_num', type=int)
parser.add_argument('market_avg_wt', type=float)
parser.add_argument('gilt_avg_wt', type=float)
parser.add_argument('discount_avg_wt', type=float)
parser.add_argument('death_avg_wt', type=float)
parser.add_argument('transport_death_avg_wt', type=float)
parser.add_argument('transfer_avg_wt', type=float)
parser.add_argument('market_avg_price_pig', type=float) #correction
parser.add_argument('gilt_avg_price_pig', type=float)
parser.add_argument('discount_avg_price_pig', type=float)
parser.add_argument('transfer_avg_price_pig', type=float)
parser.add_argument('feed_conversion', type=float)
parser.add_argument('avg_feed_cost', type=float) #addition
parser.add_argument('yield_per', type=float)
parser.add_argument('lean_per', type=float)
parser.add_argument('market_std_dev_carcass_wt', type=float)
parser.add_argument('load_avg_std_dev_carcass_wt', type=float)
parser.add_argument('feed_grinding_rate', type=float)
parser.add_argument('feed_delivery_rate', type=float)
parser.add_argument('avg_feed_delivery_ton', type=float)
parser.add_argument('trucking_market_rate', type=float)
parser.add_argument('avg_trucking_market_pig', type=float)
parser.add_argument('trucking_feeder_rate', type=float)
parser.add_argument('avg_trucking_feeder_pig', type=float)
parser.add_argument('rent_cost_week', type=float)
parser.add_argument('overhead_cost_pig', type=float)

def CreateSession():
        engine = create_engine(DB_URI)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        return DBSession()

class IngredientsApi(Resource):
    def get(self, IngrStr = 'ALL'):
        session = CreateSession()
        args = parser.parse_args()

        a_query = session.query(Ingredients.ingredient, func.sum(Ingredients.weight).label('weight'), func.sum(Ingredients.cost).label('cost'))

        if args['month_id'] is not None:
            a_query = a_query.filter(Ingredients.delivery_month == args['month_id'])
            print args['month_id']
        elif args['week_id'] is not None:
            a_query = a_query.filter(Ingredients.delivery_week == args['week_id'])
            print args['week_id']
        elif args['start_date'] is None and args['end_date'] is None:
            pass
        else:
            if args['start_date'] is None:
                args['start_date'] = date(2013,1,1)

            if args['end_date'] is None:
                args['end_date'] = date.today()

            a_query = a_query.filter(Ingredients.delivery_date.between(args['start_date'], args['end_date']))
        
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

        a_query = session.query(Groups)
        a_query = self.FilterGroup(Groups, a_query, GroupStr = GroupStr)
        group_results = a_query.all()

        schema_group = GroupsSchema(many=True)
        result_group = schema_group.dump(group_results)

        if GroupInfo is not None:
            if GroupInfo.upper() == 'INGREDIENTS':
                a_query = session.query(Ingredients.ingredient, func.sum(Ingredients.weight).label('weight'), func.sum(Ingredients.cost).label('cost'))
                a_query = a_query.group_by(Ingredients.ingredient).order_by(Ingredients.ingredient.asc())

                a_query = self.FilterGroup(Ingredients, a_query, GroupStr = GroupStr)
                query_results = a_query.all()

                schema_other = IngredientsSchema(many=True)
                result_other = schema_other.dump(query_results)
                result_group.data[0][u'ingredients'] = result_other.data

            elif GroupInfo.upper() == 'DIETS':
                a_query = session.query(Ingredients.diet, func.sum(Ingredients.weight).label('weight'), func.sum(Ingredients.cost).label('cost'))
                a_query = a_query.group_by(Ingredients.diet).order_by(Ingredients.diet.asc())

                a_query = self.FilterGroup(Ingredients, a_query, GroupStr = GroupStr)
                query_results = a_query.all()

                schema_other = IngredientsSchema(many=True)
                result_other = schema_other.dump(query_results)
                result_group.data[0][u'diets'] = result_other.data

            elif GroupInfo.upper() == 'MOVEMENTS':
                a_query = session.query(Movements.event_category.label('category'), func.sum(Movements.quantity).label('quantity'), func.sum(Movements.weight).label('weight'), func.sum(Movements.cost).label('cost'))
                a_query = a_query.group_by(Movements.event_category).order_by(Movements.event_category)

                a_query = self.FilterGroup(Movements, a_query, GroupStr = GroupStr, move_bool=True)
                query_results = a_query.all()

                schema_other = MovementsSchema(many=True)
                result_other = schema_other.dump(query_results)
                result_group.data[0][u'movements'] = result_other.data

            elif GroupInfo.upper() == 'SALES':
                a_query = session.query(Sales.group_num, func.sum(Sales.quantity).label('quantity'), func.avg(Sales.avg_live_wt).label('avg_live_wt'), func.avg(Sales.avg_carcass_wt).label('avg_carcass_wt'), func.avg(Sales.base_price_cwt).label('avg_base_price_cwt'), func.avg(Sales.vob_cwt).label('avg_vob_cwt'), func.avg(Sales.value_cwt).label('avg_value_cwt'), func.avg(Sales.yield_per).label('avg_yield_per'), func.avg(Sales.lean_per).label('avg_lean_per'))
                a_query = a_query.group_by(Sales.group_num).order_by(Sales.group_num)

                a_query = self.FilterGroup(Sales, a_query, GroupStr = GroupStr)
                query_results = a_query.all()

                schema_other = SalesSchema(many=True)
                result_other = schema_other.dump(query_results)
                result_group.data[0][u'sales'] = result_other.data

            elif GroupInfo.upper() in ['DEATHS', 'DEATH', 'REJECTS', 'EUTHANIZE', 'MARKET SALE', 'SUB-STANDARD SALE']:
                a_query = session.query(func.sum(Movements.quantity).label('quantity'), func.sum(Movements.weight).label('weight'), func.sum(Movements.cost).label('cost'), Movements.group_num)
                a_query = a_query.group_by(Movements.group_num).filter(Movements.event_category == GroupInfo)

            elif GroupInfo.upper() in ['ADJ', 'BGM', 'CON', 'DIS', 'DOT', 'GA', 'GS', 'NV', 'PWP', 'SA', 'SMS', 'SR', 'ST', 'TFP', 'WPS', 'YD']:
                a_query = session.query(func.sum(Movements.quantity).label('quantity'), func.sum(Movements.weight).label('weight'), func.sum(Movements.cost).label('cost'), Movements.group_num)
                a_query = a_query.group_by(Movements.entity).filter(Movements.event_code == GroupInfo)

        return jsonify({'groups' : result_group.data})

    def FilterGroup(self, table, query, GroupStr, move_bool = False):
        if GroupStr.upper() == 'ALL':
            a_query = query.order_by(table.group_num.desc())
        else:
            a_query = query.filter(table.group_num == GroupStr)

        return a_query

class WeightOptApi(Resource):
    def get(self):
        args = parser.parse_args()

        args['feed_pr'] = [float(x) for x in args['feed_pr']]
        args['feed_wt'] = [float(x) for x in args['feed_wt']]

        args['model_g_adj'] = [float(x) for x in args['model_g_adj']]
        args['model_fc_adj'] = [float(x) for x in args['model_fc_adj']]

        feed_cost_poly = []
        for cost in args['feed_pr']:
            feed_cost_poly.append(polynomial([cost]))

        feedCostModel = PiecePolynomial(feed_cost_poly, feed_cost_br, args['feed_wt'])

        death_poly = [polynomial(0), polynomial(w2fDeath1), polynomial(w2fDeath2), polynomial(w2fDeath3), polynomial(w2fDeath4), polynomial(w2fDeath5)]
        death_br = w2fDeath_br

        deathModel = PiecePolynomial(death_poly, death_br)

        rentModel = PiecePolynomial([polynomial(0), polynomial(args['rent'])], [0.])

        sm = SalesModel(CarcassAvg = 218, CarcassStdDev = args['carcass_std_dev'], LeanAvg = args['lean_avg'], LeanStdDev = args['lean_std_dev'], YieldAvg = args['yield_avg'], BasePrice = args['base_price'])
        gm = PigGrowthModel(awgModel, awfcModel, feedCostModel, args['model_g_adj'], args['model_fc_adj'], args['start_wt'])
        bm = BarnModel(deathModel, rentModel, gm, sm, StartNum = args['start_num'], DeathLossPer = args['death_per'], DiscountLossPer = args['discount_per'], DiscountPricePer = 50, AvgWeeksInBarn = args['weeks'])

        if args['curve'].upper() == 'OPT_PRICE':
            x = numpy.arange(250, 301, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_rev_curve(x).tolist()})
        elif args['curve'].upper() == 'OPT_PRICE_RANGE':
            x = numpy.arange(50, 111, 1)
            return jsonify({'xval' : x.tolist(), 'yval' : bm.calc_opt_price_curve(x)})

class BudgetApi(Resource):
    def get(self, GroupNum = '1505Bahl'):
        args = parser.parse_args()

        if args['budget_type'] is None:
            args['budget_type'] = 'target'

        session = CreateSession()
        budget_results = session.query(Budgets).filter( (Budgets.group_num == GroupNum) & (Budgets.budget_type == args['budget_type'].lower()) ).all()

        schema = BudgetsSchema(many=True)
        result = schema.dump(budget_results)

        return jsonify({'budget' : result.data})

class ReportCardApi(Resource):
    def get(self):
        args = parser.parse_args()

        awgModelAdjust = [args['market_avg_wt'], 0, args['wof_avg'] + 6]
        awfcModelAdjust = [args['feed_conversion'], 0, args['wof_avg'] + 6]
        feedCostModel = PiecePolynomial([args['avg_feed_cost']], [], [])

        gm = PigGrowthModel(awgModel, awfcModel, feedCostModel, awgModelAdjust, awfcModelAdjust, args['start_avg_wt'])
        
        report_card = {}
        report_card['actual'] = {}
        report_card['norm'] = {}

        session = CreateSession()
        budget_results = session.query(Budgets).filter( (Budgets.group_num == args['group_num']) & (Budgets.budget_type == 'target') ).all()
        schema = BudgetsSchema(many=True)
        result = schema.dump(budget_results)

        group_budget = simplejson.loads(simplejson.dumps(result.data[0]))

        rc_dict = simplejson.load(open("FlaskWebProject\\static\\storage\\report_card_struc.txt"))

        wt_produced = ( ( args['market_num'] * args['market_avg_wt'] ) + ( args['death_num'] * args['death_avg_wt'] ) + ( args['discount_num'] * args['discount_avg_wt'] ) + ( args['transport_death_num'] * args['transport_death_avg_wt'] ) ) - ( args['start_num'] * args['start_avg_wt'] )

        start_diff = args['start_num'] - group_budget['start_num']
        rc_dict['tot']['start_qty']['sub']['rent']['cost'] = round( ( ( args['rent_cost_week'] * args['wof_tot'] ) / group_budget['start_num'] ) * start_diff , 2 )
        rc_dict['tot']['start_qty']['sub']['pig_value']['cost'] = round( ( start_diff * ( args['market_num'] / args['start_num'] ) * ( args['market_avg_price_pig'] - gm.feed_cost_total(args['wof_avg']) - args['start_avg_price_pig'] ) ) +
                                                          start_diff * ( args['discount_num'] / args['start_num'] ) * ( args['discount_avg_price_pig'] - gm.feed_cost_total(args['wof_avg']) + gm.feed_cost_total(gm.wt_total.weeks(args['discount_avg_wt'])) - args['start_avg_price_pig'] ), 2 )

        death_diff = round( ( ( group_budget['death_num'] / group_budget['start_num'] ) - ( args['death_num'] / args['start_num'] ) ) * args['start_num'] , 0 )
        rc_dict['tot']['death_loss']['sub']['pig_value']['cost'] = round( death_diff * ( args['market_avg_price_pig'] - gm.feed_cost_total(args['wof_avg']) + gm.feed_cost_total(gm.wt_total.weeks(args['death_avg_wt'])) ) , 2 )

        discount_diff = round( ( ( group_budget['discount_num'] / group_budget['start_num'] ) - ( args['discount_num'] / args['start_num'] ) ) * args['start_num'] , 0 )
        rc_dict['tot']['discount_loss']['sub']['pig_value']['cost'] = round( discount_diff * ( args['market_avg_price_pig'] - args['discount_avg_price_pig'] - gm.feed_cost_total(args['wof_avg']) + gm.feed_cost_total(gm.wt_total.weeks(args['discount_avg_wt'])) ) , 2 )

        transport_death_diff = round( ( ( group_budget['transport_death_num'] / group_budget['start_num'] ) - ( args['transport_death_num'] / args['start_num'] ) ) * args['start_num'] , 0 )
        rc_dict['tot']['transport_death_loss']['sub']['pig_value']['cost'] = round( transport_death_diff * args['market_avg_price_pig'] , 2 )

        feed_diff = ( wt_produced * ( group_budget['feed_conversion'] - args['feed_conversion'] ) )
        rc_dict['tot']['feed_conversion']['sub']['feed_grinding']['cost'] = round( ( feed_diff / 2000 ) * args['feed_grinding_rate'] , 2 )
        rc_dict['tot']['feed_conversion']['sub']['feed_delivery']['cost'] = round( ( ( feed_diff / 2000 ) / args['avg_feed_delivery_ton'] ) * args['feed_delivery_rate'] , 2 )
        rc_dict['tot']['feed_conversion']['sub']['feed_value']['cost'] = round( feed_diff * args['avg_feed_cost'] , 2 )

        for total in rc_dict['tot']:
            for sub_total in rc_dict['tot'][total]['sub']:
                rc_dict['tot'][total]['sub'][sub_total]['cost_pig'] = round( rc_dict['tot'][total]['sub'][sub_total]['cost'] / args['start_num'] , 2 )
                rc_dict['tot'][total]['total_cost'] = rc_dict['tot'][total]['total_cost'] + rc_dict['tot'][total]['sub'][sub_total]['cost']
                rc_dict['tot'][total]['total_cost_pig'] = rc_dict['tot'][total]['total_cost_pig'] + rc_dict['tot'][total]['sub'][sub_total]['cost_pig']

            rc_dict['grand_total_cost'] = rc_dict['grand_total_cost'] + rc_dict['tot'][total]['total_cost']
            rc_dict['grand_total_cost_pig'] = rc_dict['grand_total_cost_pig'] + rc_dict['tot'][total]['total_cost_pig']

        return jsonify({'report_card' : rc_dict})