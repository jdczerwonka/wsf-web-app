from marshmallow import Schema, fields

class DietsSchema(Schema):
    diet = fields.Str()
    quantity = fields.Decimal(2)
    cost = fields.Decimal(2)

class IngredientsSchema(Schema):
    ingredient = fields.Str()
    quantity = fields.Decimal(2)
    cost = fields.Decimal(2)

class MovementsSchema(Schema):
    category = fields.Str()
    quantity = fields.Int()
    weight = fields.Decimal(2)
    cost = fields.Decimal(2)

class SalesSchema(Schema):
    group_num = fields.Str()
    quantity = fields.Int()
    avg_live_wt = fields.Decimal(2)
    avg_carcass_wt = fields.Decimal(2)
    avg_base_price_cwt = fields.Decimal(2)
    avg_vob_cwt = fields.Decimal(2)
    avg_yield_per = fields.Decimal(2)
    avg_lean_per = fields.Decimal(2)

class GroupsSchema(Schema):
    group_num = fields.Str()
    group_type = fields.Str()
    status = fields.Str()
    producer = fields.Str()
    site = fields.Str()
    barn = fields.Str()
    open_date = fields.Date()
    close_date = fields.Date()
    ingredients = fields.Nested(IngredientsSchema)
    movements = fields.Nested(MovementsSchema)