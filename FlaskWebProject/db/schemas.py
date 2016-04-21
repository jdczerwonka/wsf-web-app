from marshmallow import Schema, fields

class IngredientsSchema(Schema):
    diet = fields.Str()
    ingredient = fields.Str()
    weight = fields.Decimal(2)
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
    avg_value_cwt = fields.Decimal(2)
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
    diets = fields.Nested(IngredientsSchema)
    movements = fields.Nested(MovementsSchema)
    sales = fields.Nested(SalesSchema)