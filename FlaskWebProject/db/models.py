from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mssql import VARCHAR, TINYINT, SMALLINT, DATE, DECIMAL, MONEY, SMALLMONEY, BIGINT, INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Diets(Base):
    __tablename__ = 'diets'

    id = Column(BIGINT, primary_key=True)
    order_id = Column(VARCHAR(25))
    group_num = Column(VARCHAR(25), ForeignKey('groups.group_num'))
    mill = Column(VARCHAR(50))
    delivery_date = Column(DATE)
    delivery_month = Column(VARCHAR(7))
    delivery_week = Column(VARCHAR(7))
    year = Column(SMALLINT)
    month = Column(TINYINT)
    week = Column(TINYINT)
    diet = Column(VARCHAR(50))
    quantity = Column(DECIMAL(9,2))
    cost = Column(MONEY)

class Ingredients(Base):
    __tablename__ = 'ingredients'

    id = Column(BIGINT, primary_key=True)
    order_id = Column(VARCHAR(25))
    group_num = Column(VARCHAR(25), ForeignKey('groups.group_num'))
    mill = Column(VARCHAR(50))
    delivery_date = Column(DATE)
    delivery_month = Column(VARCHAR(7))
    delivery_week = Column(VARCHAR(7))
    year = Column(SMALLINT)
    month = Column(TINYINT)
    week = Column(TINYINT)
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

class Movements(Base):
    __tablename__ = 'movements'

    id = Column(BIGINT, primary_key=True)
    entity_to = Column(VARCHAR(50))
    entity_type_to = Column(VARCHAR(20))
    event_category_to = Column(VARCHAR(50))
    event_code_to = Column(VARCHAR(10))
    event_name_to = Column(VARCHAR(50))
    entity_from = Column(VARCHAR(50))
    entity_type_from = Column(VARCHAR(20))
    event_category_from = Column(VARCHAR(50))
    event_code_from = Column(VARCHAR(10))
    event_name_from = Column(VARCHAR(50))
    movement_date = Column(DATE)
    movement_month = Column(VARCHAR(7))
    movement_week = Column(VARCHAR(7))
    year = Column(SMALLINT)
    month = Column(TINYINT)
    week = Column(TINYINT)
    quantity = Column(SMALLINT)
    weight = Column(INTEGER)
    cost = Column(MONEY)

class Sales(Base):
    __tablename__ = 'sales'

    id = Column(BIGINT, primary_key=True)
    group_num = Column(VARCHAR(25), ForeignKey('groups.group_num'))
    plant = Column(VARCHAR(100))
    tattoo = Column(SMALLINT)
    kill_date = Column(DATE)
    kill_month = Column(VARCHAR(7))
    kill_week = Column(VARCHAR(7))
    year = Column(SMALLINT)
    month = Column(TINYINT)
    week = Column(TINYINT)
    quantity = Column(TINYINT)
    avg_live_wt = Column(DECIMAL(5,2))
    avg_carcass_wt = Column(SMALLINT)
    base_price_cwt = Column(SMALLMONEY)
    vob_cwt = Column(SMALLMONEY)
    value_cwt = Column(SMALLMONEY)
    base_price = Column(SMALLMONEY)
    vob = Column(SMALLMONEY)
    value = Column(SMALLMONEY)
    back_fat = Column(DECIMAL(5, 3))
    loin_depth = Column(DECIMAL(5, 3))
    yield_per = Column(DECIMAL(4, 2))
    lean_per = Column(TINYINT)
    
