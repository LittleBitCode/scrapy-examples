# -*- coding: utf-8 -*-
import scrapy
from scrapy import Selector
import redis
from pymongo import MongoClient

class PhantomjsSpider(scrapy.Spider):
    name = 'phantomjs'
    allowed_domains = ['baidu.com']
    start_urls = [
        'http://baidu.com/'
    ]



    def parse(self, response):
        #mongodb
        client = MongoClient('127.0.0.1', 27017)
        db = client.spiders
        users = db['users']
        rs = users.find_one()
        print('------ mongodb ------')
        print(rs['name'])
        print('------ mongodb ------')

        #redis
        r = redis.Redis(host='127.0.0.1',port=6379)
        print('------ redis ------')
        print(r['name'])
        print('------ redis ------')

        # selector = Selector(text=response.body)
        # print(selector.xpath('//title/text()').extract())
        # yield