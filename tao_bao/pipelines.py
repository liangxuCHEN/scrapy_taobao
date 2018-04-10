# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from tao_bao.db.dbhelper import TaoBaoModel, engine
# from scrapy.exceptions import DropItem
from datetime import datetime
import copy


# 存储到数据库
class DataBasePipeline(object):
    def open_spider(self, spider):
        self.items = []

    def process_item(self, item, spider):
        # item 用的是同一个地址，需要copy才能避免后面的修改
        item['record_date'] = datetime.strptime(item['record_date'], "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        item['is_tmall'] = int(item['is_tmall'] == 'true')
        item['pay_person'] = int(item['pay_person'])
        item['price'] = float(item['price'])
        if item['province'] == '':
            item['province'] = item['city']
        self.items.append(copy.deepcopy(item))

    def close_spider(self, spider):
        conn = engine.connect()
        try:
            conn.execute(TaoBaoModel.__table__.insert(), self.items)
        except Exception as e:
            print('插入数据出错， 错误信息：%s' % e)
        finally:
            conn.close()