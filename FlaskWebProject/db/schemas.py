from marshmallow import Schema, fields

class IngredientsSchema(Schema):
    ingredient = fields.Str()
    quantity = fields.Decimal(2)
    cost = fields.Decimal(2)

class GroupsSchema(Schema):
    group_num = fields.Str()
    group_type = fields.Str()
    status = fields.Str()
    producer = fields.Str()
    site = fields.Str()
    barn = fields.Str()
    open_date = fields.Date()
    close_date = fields.Date()
    death_num = fields.Decimal(2)
    weight = fields.Decimal(2)
    quantity = fields.Decimal(2)
    cost = fields.Decimal(2)