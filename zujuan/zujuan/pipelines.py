# pipelines.py
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import logging
import json
import re
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import codecs
import requests
import os
from zujuan.items import ImageItem,ExerciseItem
import time

class DownloadImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        image_urls = {
            'answer': item['answer'],
            'method': item['method']
        }
        for key in dict(image_urls).keys():
            if image_urls[key] != None and str(image_urls[key]).startswith('http'):
                print('-------------  开始下载图片%s -----------' % ( image_urls[key]))
                yield Request(
                    image_urls[key],
                    meta={
                        'item': item,
                        'key' : key
                    }
                )  # 添加meta是为了下面重命名文件名使用

    # 重写保存图片路径方法
    def file_path(self, request, response=None, info=None):
        item        = request.meta['item']
        paper       = item['paper']
        firstFolder = request.meta['key']
        image_guid  = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        name        = item['source_id']
        ext         = str(request.url.split('/')[-1].split('.')[-1]).split('?')[0]
        image_name  = name + '.' + ext
        filename    = u'{0}/{1}/{2}'.format(paper['site_id'],firstFolder, image_name)
        return filename

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]  # ok判断是否下载成功
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        for image_path in image_paths:
            folder = str(image_path).split('/')[1]
            if folder == 'answer':
                item['answer'] = image_path
            elif folder == 'method':
                item['method'] = image_path
        print('------------ 图片下载完成 %s ------------' % image_paths)
        return item


class ocrPipeline(object):

    pass

class ZujuanPipeline(object):
    paper_sql = """
                   insert into papers(`title`,`site_id`,`year`,`level`,`subject`,`grade`,`type`,`exercise_num`,`views`,`uploaded_at`,`url`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
    exercise_sql = """
                      insert into exercises(`subject`,`type`,`degree`,`source_id`,`paper_id`,`description`,`method_img`,`answer_img`,`options`,`points`,`url`,`sort`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
    paper_update_sql = """
                          update papers set `exercise_num` = %s where `url` = %s
                       """

    def __init__(self, settings):
        self.settings = settings

    def process_item(self, item, spider):
        if spider.name == 'zujuan' or spider.name == 'zxls':
            # 先判断试卷是否已经存在
            paper = item['paper']
            self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
            row = self.cursor.fetchone()
            print('===================')
            print('rowcount:%s' % self.cursor.rowcount)
            print('===================')
            if self.cursor.rowcount == 0:
                self.cursor.execute(self.paper_sql,
                                    (paper['title'],
                                     paper['site_id'],
                                     paper['year'],
                                     paper['level'],
                                     paper['subject'],
                                     paper['grade'],
                                     paper['type'],
                                     paper['exercise_num'],
                                     paper['views'],
                                     paper['uploaded_at'],
                                     paper['url'])
                                    )
                paper_id = self.cursor.lastrowid
            else:
                if spider.name == 'zujuan':
                    self.cursor.execute(self.paper_update_sql,(paper['exercise_num'],paper['url']))
                paper_id = row[0]

            print(">>>>>>>>>>>>>>>>>>>>>>>> new paper id: %s <<<<<<<<<<<<<<<<<<<<<<<<" % (paper_id))
            # 写入试题表
            self.cursor.execute(self.exercise_sql, (
                    item['subject'],
                    item['type'],
                    item['degree'],
                    item['source_id'],
                    paper_id,
                    item['description'],
                    # pymysql.escape_string(item['method']),
                    item['method'],
                    # pymysql.escape_string(item['answer']),
                    item['answer'],
                    item['options'],
                    item['points'],
                    item['url'],
                    item['sort']
                )
            )
            print(">>>>>>>>>>>>>>>>>>>>>>>> store success <<<<<<<<<<<<<<<<<<<<<<<<")
        else:
            spider.log('Undefined name: %s' % spider.name)

        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):
        # 连接数据库
        self.connect    = pymysql.connect(
            host        = self.settings.get('MYSQL_HOST'),
            port        = self.settings.get('MYSQL_PORT'),
            db          = self.settings.get('MYSQL_DBNAME'),
            user        = self.settings.get('MYSQL_USER'),
            passwd      = self.settings.get('MYSQL_PASSWD'),
            charset     = 'utf8',
            use_unicode = True
        )

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()
        self.cursor.execute('SET NAMES utf8')
        self.cursor.execute('SET CHARACTER SET utf8')
        self.cursor.execute('SET CHARACTER_SET_CONNECTION=utf8')
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
