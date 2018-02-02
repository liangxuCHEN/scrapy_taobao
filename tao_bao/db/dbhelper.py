# -*- coding: utf-8 -*-
from scrapy.utils.project import get_project_settings  #导入seetings配置
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

# 初始化数据库连接:
# engine = create_engine('mysql+pymysql://root:123asd@localhost:3306/utf_sys?charset=utf8')
engine = create_engine('postgresql+psycopg2://postgres:123asd@192.168.0.186/execdb')

# 初始化redis数据库连接
Redis = redis.StrictRedis(host='localhost',port=6379,db=0)

Base = declarative_base()


class TaoBaoModel(Base):
    __tablename__ = 'tab_taobao_item'

    id = Column(Integer, primary_key=True)
    page_number = Column(Integer)
    job_id = Column(String(50))
    item_id = Column(String(50))
    name = Column(String(100))
    main_pic = Column(String(200))
    price = Column(Float)
    pay_person = Column(Integer)
    province = Column(String(20))
    city = Column(String(20))
    shop_name = Column(String(50))
    detail_url = Column(String(200))
    category_id = Column(String(50))
    category = Column(String(50))
    is_tmall = Column(Integer)
    user_id = Column(String(50))
    market = Column(String(20))
    record_date = Column(DateTime)


#创建数据表，如果数据表存在则忽视！！！
Base.metadata.create_all(engine)
