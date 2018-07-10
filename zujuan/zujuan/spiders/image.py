# -*- coding: utf-8 -*-
import scrapy
import json
from zujuan.items import ImageItem

class ImageSpider(scrapy.Spider):
    name = 'image'
    start_urls = ["http://jandan.net/ooxx"]

    def parse(self, response):
        item = ImageItem()
        item['image_urls'] = response.xpath('//img//@src').extract()  # 提取图片链接
        yield item
