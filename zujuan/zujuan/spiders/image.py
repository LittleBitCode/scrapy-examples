# -*- coding: utf-8 -*-
import scrapy
import json
from zujuan.items import ImageItem
from aip import AipOcr
import zujuan.settings as set

class ImageSpider(scrapy.Spider):
    name = 'image'
    start_urls = ["http://jandan.net/ooxx"]

    def parse(self, response):
        item = ImageItem()
        item['image_urls'] = response.xpath('//img//@src').extract()  # 提取图片链接
        yield item


#运行此处 查看百度图片识别结果
if __name__ == '__main__':
    def get_file_content(filePath):
        with open(filePath,'rb') as fp:
            return fp.read()

    client = AipOcr(set.BAIDUAPI['APP_ID'], set.BAIDUAPI['API_KEY'], set.BAIDUAPI['SECRET_KEY'])

    # image = get_file_content('/Users/zhengchaohua/Desktop/Python/scrapy-examples/zujuan/zujuan/zujuan_21cnjy/method/1233402_1.png')
    image = get_file_content('/Users/zhengchaohua/Desktop/3B6CA8847B9A68F67D047B07A9DD75C5.png')
    result = client.basicAccurate(image)
    result_words = ''
    if int(result['words_result_num']) > 0:
        for words in result['words_result']:
            result_words += words['words']
    print(result_words)






