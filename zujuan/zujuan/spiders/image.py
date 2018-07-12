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



if __name__ == '__main__':
    def get_file_content(filePath):
        with open(filePath,'rb') as fp:
            return fp.read()

    client = AipOcr(set.BAIDUAPI['APP_ID'], set.BAIDUAPI['API_KEY'], set.BAIDUAPI['SECRET_KEY'])

    image = get_file_content('/users/zhengchaohua/desktop/myProject/Examples/zujuan/zujuan/2/method/1213386.png')
    result = client.basicAccurate(image)
    result_words = []
    if int(result['words_result_num']) > 0:
        for words in result['words_result']:
            result_words.append(words['words'])
            print(words['words'])

    print(result_words)
    # return result_words
    # if int(result['words_result_num']) > 0:
    #     for words in result['words_result']:
            # print(words['words'])






