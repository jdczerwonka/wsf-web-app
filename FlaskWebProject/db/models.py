from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mssql import VARCHAR, TINYINT, SMALLINT, DATE, DECIMAL, MONEY, BIGINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Diets(Base):
    __tablename__ = 'diets'

    order_id = Column(VARCHAR(25), primary_key=True)
    group_num = Column(VARCHAR(25), ForeignKey('groups.group_num'))
    group_type = Column(VARCHAR(25))
    delivery_date = Column(DATE)
    delivery_month = Column(VARCHAR(7))
    delivery_week = Column(VARCHAR(7))
    year = Column(SMALLINT)
    month = Column(TINYINT)
    week = Column(TINYINT)
    producer = Column(VARCHAR(50))
    site = Column(VARCHAR(50))
    mill = Column(VARCHAR(50))
    diet = Column(VARCHAR(50))
    quantity = Column(DECIMAL(9,2))
    cost = Column(MONEY)

class Ingredients(Base):
    __tablename__ = 'diet_ingredients'

    id = Column(BIGINT, primary_key=True)
    order_id = Column(VARCHAR(25), ForeignKey('diets.order_id'))
    ingredient = Column(VARCHAR(50))
    quantity = Column(DECIMAL(8,2))
    cost = Column(MONEY)

class Groups(Base):
    __tablename__ = 'groups'

    group_num = Column(VARCHAR(25), primary_key=True)
    group_type = Column(VARCHAR(25))
    status = Column(VARCHAR(25))
    producer = Column(VARCHAR(50))
    site = Column(VARCHAR(50))
    barn = Column(VARCHAR(50))
    open_date = Column(DATE)
    close_date = Column(DATE)