# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaoBaoItem(scrapy.Item):
    page_number = scrapy.Field()
    job_id = scrapy.Field()
    item_id = scrapy.Field()
    name = scrapy.Field()
    main_pic = scrapy.Field()
    price = scrapy.Field()
    pay_person = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    shop_name = scrapy.Field()
    record_date = scrapy.Field()
    detail_url = scrapy.Field()
    category_id = scrapy.Field()
    category = scrapy.Field()
    is_tmall = scrapy.Field()
    user_id = scrapy.Field()
    market = scrapy.Field()

