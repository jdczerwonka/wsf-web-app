from marshmallow import Schema, fields

class IngredientsSchema(Schema):
    ingredient = fields.Str()
    quantity = fields.Decimal(2)
    cost = fields.Decimal(2)