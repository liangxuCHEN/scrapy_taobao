from scrapy.spiders import Spider
from scrapy import Request
from tao_bao.items import TaoBaoItem
import re
import time
import datetime
import requests
from tao_bao.db.dbhelper import engine, TaoBaoProjectModel
from sqlalchemy.orm import sessionmaker
# 如果有目录代码
# df = pd.read_csv('/spiders/taoBaoCategory.csv')


Session_Class = sessionmaker(bind=engine)  # 创建与数据库的会话，Session_Class为一个类

Session = Session_Class()  # 实例化与数据库的会话

"""
需要查找信息列表

参数说明：

id: 这个搜索项目的ID,（TODO：以后在数据库生成）
market： 1 --》 淘宝， 2 --》 天猫
key_word: 输入搜索框的关键字
page_number： 需要爬取的页数，最大100页
min_price： 选填，搜索得到宝贝价格的最低价
max_price: 选填，搜索得到宝贝价格的最高价
project_name: 项目名称
"""
# TODO:数据库获取新项目
search_parameter = [
    {'project_name':'20180202_jacket', 'market': '', 'min_price':'', 'max_price':'', 'key_word': '夹克', 'page_number': 2}
]



class TBSpider(Spider):
    """
    淘宝搜索页面的信息爬取，结果按照人气排序
    TODO： 可以增加其他几种排序，有综合，销量，信用
    """
    name = 'taoBaoSpider'
    allowed_domains = ["taobao.com"]
    start_urls = ['http://taobao.com/']


    def parse(self, response):
        current_time = datetime.datetime.now().strftime('%Y%m%d')

        for data in search_parameter:

            # 把项目添加到数据库
            # TODO: 如果在数据库拿的项目就是update
            data['created'] = current_time
            taobao_project = TaoBaoProjectModel(**data)
            taobao_project.status = 'running'
            Session.add(taobao_project)
            Session.commit()

            key = str(data['key_word'])

            if ' ' in key:
                key = ''.join(key.split())

            for i in range(0,int(data['page_number'])):

                allPidDetailData = []
                if i==0:
                    try:
                        if len(str(data['min_price'])) > 0 or len(str(data['max_price'])) > 0:

                            if str(data['market']) == '2':
                                lastUrl = "https://s.taobao.com/api?ajax=true&m=customized&" \
                                          "stats_click=search_radio_all:1&bcoffset=0&js=1&sort=renqi-desc&" \
                                          "filter_tianmao=tmall&filter=reserve_price[{min_price},{max_price}]&" \
                                          "q={key}&s=36&initiative_id=staobaoz_{current_time}&" \
                                          "ie=utf8".format(min_price=str(data['min_price']),
                                                           max_price=str(data['max_price']),
                                                           key=str(key),
                                                           current_time=str(current_time))
                            else:
                                # 有最高也有低
                                lastUrl = 'https://s.taobao.com/api?ajax=true&m=customized&' \
                                          'stats_click=search_radio_all:1&bcoffset=0&js=1&' \
                                          'sort=renqi-desc&filter=reserve_price[{min_price},{max_price}]&' \
                                          'q={key}&s=36&initiative_id=staobaoz_{current_time}&' \
                                          'ie=utf8'.format(min_price=str(data['min_price']),
                                                           max_price=str(data['max_price']),
                                                           key=str(key),
                                                           current_time=str(current_time))
                        else:
                            # 第一页最后12个产品
                            if str(data['market']) == '2':
                                lastUrl = 'https://s.taobao.com/api?ajax=true&m=customized&bcoffset=0&js=1&' \
                                          'sort=renqi-desc&q={key}&ntoffset=4&filter_tianmao=tmall&' \
                                          's=36&initiative_id=staobaoz_{current_time}&' \
                                          'ie=utf8'.format(key=str(key), current_time=str(current_time))
                            else:
                                lastUrl = 'https://s.taobao.com/api?ajax=true&m=customized&bcoffset=0&js=1&' \
                                          'sort=renqi-desc&q={key}&ntoffset=4&s=36&' \
                                          'initiative_id=staobaoz_{current_time}&' \
                                          'ie=utf8'.format(key=str(key), current_time=str(current_time))

                        req = requests.get(lastUrl)
                        babyInfo = req.json()
                        itemList = babyInfo['API.CustomizedApi']['itemlist']['auctions']
                        for j in range(0,len(itemList)):
                            taoBaoItem = TaoBaoItem()
                            taoBaoItem['page_number'] = i
                            taoBaoItem['job_id'] = str(data['project_name'])
                            taoBaoItem['item_id'] = itemList[j]['nid']

                            allPidDetailData.append(itemList[j]['nid'])
                            if str(data['market']) == '2':
                                taoBaoItem['detail_url'] = "https://detail.tmall.com/item.htm?id="+ str(itemList[j]['nid'])
                                taoBaoItem['market'] = '天猫'
                            else:
                                if itemList[j]['detail_url'].find('tmall') == -1:
                                    taoBaoItem['detail_url'] = "https://item.taobao.com/item.htm?id=" + str(itemList[j]['nid'])
                                    taoBaoItem['market'] = '淘宝'
                                else:
                                    taoBaoItem['detail_url'] = "https://detail.tmall.com/item.htm?id=" + str(itemList[j]['nid'])
                                    taoBaoItem['market'] = '天猫'


                            taoBaoItem['name'] = itemList[j]['raw_title']
                            taoBaoItem['main_pic'] = 'https:'+itemList[j]['pic_url']
                            taoBaoItem['price'] = itemList[j]['view_price']


                            viewSales = str(itemList[j].get('view_sales'))
                            if u'人付款' in viewSales:
                                # try:
                                viewSales = viewSales.replace(u'人付款','')
                                taoBaoItem['pay_person'] = viewSales
                                # except Exception as e:
                                #     print e
                            else:
                                taoBaoItem['pay_person'] = itemList[j].get('view_sales')

                            taoBaoItem['shopName'] = itemList[j]['nick']
                            taoBaoItem['category_id'] = itemList[j].get('category')
                            taoBaoItem['is_tmall'] = itemList[j].get('shopcard').get('isTmall')
                            taoBaoItem['user_id'] = itemList[j].get('user_id')
                            # 有目录编码对应表可以做这个
                            # for k in range(0,len(df)):
                            #     if str(df['CategoryId'][k]) == itemList[j]['category']:
                            #         taoBaoItem['category'] = str(df['CategoryName'][k])
                            #         break
                            #     else:
                            taoBaoItem['category'] = '-'
                            provString = ''
                            cityStr = ''
                            if ' ' in itemList[j]['item_loc'] and len(itemList[j]['item_loc']) > 0:
                                alladdressData = itemList[j]['item_loc'].split(' ')
                                provString = alladdressData[0]
                                cityStr = alladdressData[1]
                            else:
                                provString = ' '
                                cityStr = itemList[j]['item_loc']

                            taoBaoItem['province'] = provString
                            taoBaoItem['city'] = cityStr
                            taoBaoItem['record_date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))

                            yield taoBaoItem
                    except Exception as e:
                        print('HERE --------------%s'%e)


                # 有上限和下限价格的URL
                if len(str(data['min_price']))>0 and len(str(data['max_price']))>0:
                    if str(data['market']) == '2':
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&ie=utf8&' \
                              'initiative_id=tbindexz_{current_time}&fs=1&filter_tianmao=tmall&sort=renqi-desc' \
                              '&bcoffset=0&filter=reserve_price%5B{min_price}%2C{max_price}%5D&' \
                              's={number}'.format(min_price=str(data['min_price']),
                                                  max_price=str(data['max_price']),
                                                  key=str(key),
                                                  current_time=str(current_time),
                                                  number=str(44*i))
                    else:
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&js=1&' \
                              'stats_click=search_radio_all%3A1&initiative_id=staobaoz_{current_time}&ie=utf8' \
                              '&sort=renqi-desc&filter=reserve_price%5B{min_price}%2C{max_price}%5D&' \
                              'bcoffset=4&ntoffset=4&p4ppushleft=2%2C48&' \
                              's={number}'.format(min_price=str(data['min_price']),
                                                  max_price=str(data['max_price']),
                                                  key=str(key),
                                                  current_time=str(current_time),
                                                  number=str(44*i))

                elif len(str(data['min_price']))>0 and len(str(data['max_price']))==0:
                    if str(data['market']) == '2':
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&ie=utf8&' \
                              'initiative_id=tbindexz_{current_time}&fs=1&filter_tianmao=tmall&sort=renqi-desc&' \
                              'bcoffset=0&filter=reserve_price%5B{max_price}%2C%5D&' \
                              's={number}'.format(min_price=str(data['min_price']),
                                                  max_price=str(data['max_price']),
                                                  key=str(key),
                                                  current_time=str(current_time),
                                                  number=str(44*i))
                    else:
                        # 只有最低，没有最高
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&js=1&' \
                              'stats_click=search_radio_all%3A1&initiative_id=staobaoz_{current_time}&ie=utf8' \
                              '&sort=renqi-desc&filter=reserve_price%5B{min_price}%2C%5D&' \
                              'bcoffset=4&ntoffset=4&p4ppushleft=2%2C48&' \
                              's={number}'.format(min_price=str(data['min_price']),
                                                  key=str(key),
                                                  current_time=str(current_time),
                                                  number=str(44*i))

                elif len(str(data['min_price'])) ==0 and len(str(data['max_price']))>0:
                    # 只有最高，没有最低
                    if str(data['market']) == '2':
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&ie=utf8&' \
                              'initiative_id=tbindexz_{current_time}&fs=1&filter_tianmao=tmall&' \
                              'sort=renqi-desc&bcoffset=0&filter=reserve_price%5B%2C{max_price}%5D&' \
                              's={number}'.format(max_price=str(data['max_price']),
                                                  key=str(key),
                                                  current_time=str(current_time),
                                                  number=str(44*i))
                    else:
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&js=1&' \
                              'stats_click=search_radio_all%3A1&initiative_id=staobaoz_{current_time}&ie=utf8' \
                              '&sort=renqi-desc&filter=reserve_price%5B%2C{max_price}%5D&bcoffset=4&ntoffset=4&' \
                              'p4ppushleft=2%2C48&s={number}'.format(max_price=str(data['max_price']),
                                                                     key=str(key),
                                                                     current_time=str(current_time),
                                                                     number=str(44*i))

                else:
                    # 没有最高也没有最低
                    if str(data['market']) == '2':
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&ie=utf8&' \
                              'initiative_id=tbindexz_{current_time}&fs=1&filter_tianmao=tmall&sort=renqi-desc&' \
                              'bcoffset=0&s={number}'.format(key=str(key),
                                                             current_time=str(current_time),
                                                             number=str(44*i))

                    else:
                        url = 'https://s.taobao.com/search?q={key}&imgfile=&js=1&stats_click=search_radio_all%3A1&' \
                              'initiative_id=staobaoz_{current_time}&ie=utf8&sort=renqi-desc&bcoffset=4&ntoffset=4&' \
                              'p4ppushleft=2%2C48&s={number}'.format(key=str(key),
                                                                     current_time=str(current_time),
                                                                     number=str(44*i))
                yield Request(
                    url=url,
                    callback=self.page2,
                    meta={'page':i,'productID':str(data['project_name']),'market':data['market']}
                )

            # 更新状态
            TaoBaoProjectModel.query.filter_by(id=taobao_project.id).update({'status': 'finish'})
            Session.commit()

    def page2(self,response):

        body = response.body.decode("utf-8", "ignore")
        patPic = '"pic_url":"(.*?)"'
        patid = '"nid":"(.*?)"'
        patprice = '"view_price":"(.*?)"'
        patname = '"raw_title":"(.*?)"'
        patPayPerson = '"view_sales":"(.*?)"'

        pataddress = '"item_loc":"(.*?)"'
        patShopName = '"nick":"(.*?)"'
        category = '"category":"(.*?)"'
        isTmall = '"isTmall":(.*?),'
        user_id = '"user_id":"(.*?)"'

        detailURL = '"detail_url":"(.*?)"'

        allPic = re.compile(patPic).findall(body) #图片集合
        allid = re.compile(patid).findall(body)  # 商品Id集合
        allprice = re.compile(patprice).findall(body)  # 商品价格集合
        allName = re.compile(patname).findall(body) #名字集合
        alladdress = re.compile(pataddress).findall(body)  # 商户地址集合
        allPayPerson = re.compile(patPayPerson).findall(body) #全部付款人数集合
        allShopName = re.compile(patShopName).findall(body) #店铺名称
        allCategory = re.compile(category).findall(body)
        allIsTmall = re.compile(isTmall).findall(body)
        allUserId = re.compile(user_id).findall(body)
        allDetailURL = re.compile(detailURL).findall(body)

        for j in range(0,len(allid)):
            taoBaoItem = TaoBaoItem()
            taoBaoItem['page_number'] = response.meta['page']
            taoBaoItem['job_id'] = response.meta['productID']
            taoBaoItem['item_id'] = allid[j]
            if str(response.meta['market']) == '2':
                taoBaoItem['detail_url'] = "https://detail.tmall.com/item.htm?id=" + str(allid[j])
                taoBaoItem['market'] = '天猫'
            else:
                if allDetailURL[j].find('tmall') == -1:
                    taoBaoItem['detail_url'] = "https://item.taobao.com/item.htm?id=" + str(allid[j])
                    taoBaoItem['market'] = '淘宝'
                else:
                    taoBaoItem['detail_url'] = "https://detail.tmall.com/item.htm?id=" + str(allid[j])
                    taoBaoItem['market'] = '天猫'

            taoBaoItem['name'] = allName[j]
            taoBaoItem['main_pic'] = 'https:'+allPic[j]
            taoBaoItem['price'] = allprice[j]

            viewSales = str(allPayPerson[j])
            if u'人付款' in viewSales:
                # try:
                viewSales = viewSales.replace(u'人付款', '')
                taoBaoItem['pay_person'] = viewSales
                # except Exception as e:
                #     print e
            else:
                taoBaoItem['pay_person'] = allPayPerson[j]

            taoBaoItem['shop_name'] = allShopName[j]
            taoBaoItem['category_id'] = allCategory[j]
            taoBaoItem['is_tmall'] = allIsTmall[j]
            taoBaoItem['user_id'] = allUserId[j]
            #
            # for k in range(0, len(df)):
            #     if str(df['CategoryId'][k]) == allCategory[j]:
            #         taoBaoItem['category'] = str(df['CategoryName'][k])
            #         break
            #     else:
            taoBaoItem['category'] = '-'

            provString = ''
            cityStr = ''
            if ' ' in alladdress[j] and len(alladdress[j])>0:
                alladdressData = alladdress[j].split(' ')
                provString = alladdressData[0]
                cityStr = alladdressData[1]
            else:
                provString=' '
                cityStr = alladdress[j]

            taoBaoItem['province'] = provString
            taoBaoItem['city'] = cityStr
            taoBaoItem['record_date'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))

            yield taoBaoItem

