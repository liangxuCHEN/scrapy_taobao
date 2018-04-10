# -*- coding: utf-8 -*-
from scrapy.utils.project import get_project_settings  #导入seetings配置
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, func
from sqlalchemy.ext.declarative import declarative_base
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


#做一个表记录搜索历史
class TaoBaoProjectModel(Base):
    """
    参数说明：

    _id: 这个搜索项目的ID, （TODO：以后在数据库生成)
    project_name: 项目名称
    market： 1 - -》 淘宝， 2 - -》 天猫
    keyword: 输入搜索框的关键字
    pageNumber： 需要爬取的页数，最大100页
    min_price： 选填，搜索得到宝贝价格的最低价
    max_price: 选填，搜索得到宝贝价格的最高价
    status: 1：新任务， 2：进行中， 3：已经完成
    created： 创建时间
    """

    __tablename__ = 'tab_project'

    id = Column(Integer, primary_key=True)
    market = Column(String(10))
    project_name = Column(String(50))
    key_word = Column(String(200))
    page_number = Column(Integer)
    min_price = Column(String(20))
    max_price = Column(String(20))
    status = Column(String(20), server_default='new')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


    def to_json(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'market': self.market,
            'key_word': self.key_word,
            'page_number': self.page_number,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'status': self.status,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at is not None else "",
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at is not None else ""

        }


#创建数据表，如果数据表存在则忽视！！！
Base.metadata.create_all(engine)