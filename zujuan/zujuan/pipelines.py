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

class DownloadImagesPipeline(ImagesPipeline):

    #重写保存图片路径方法
    # def file_path(self, request, response=None, info=None):
    #     """
    #     :param request: 每一个图片下载管道请求
    #     :param response:
    #     :param info:
    #     :param strip :清洗Windows系统的文件夹非法字符，避免无法创建目录
    #     :return: 每套图的分类目录
    #     """
    #     item = request.meta['item']
    #     FolderName = item['name']
    #     image_guid = request.url.split('/')[-1]
    #     filename = u'full/{0}/{1}'.format(FolderName, image_guid)
    #     return filename

    def get_media_requests(self, item, info):
        print('1111111111111111111111111111111')
        return
        # for image_url in item['image_urls']:
        #     image_url = "http://" + image_url
        #     yield Request(image_url)

    def item_completed(self, results, item, info):
        print('22222222222222222222222222222')
        # image_paths = [x['path'] for ok, x in results if ok]  # ok判断是否下载成功
        # if not image_paths:
        #     raise DropItem("Item contains no images")
        # item['image_paths'] = image_paths
        return item


class ZujuanPipeline(object):
    paper_sql = """
                   insert into papers(`title`,`site_id`,`year`,`level`,`subject`,`grade`,`type`,`exercise_num`,`views`,`uploaded_at`,`url`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
    exercise_sql = """
                      insert into exercises(`subject`,`type`,`degree`,`source_id`,`paper_id`,`description`,`method`,`answer`,`options`,`points`,`url`,`sort`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
    paper_update_sql = """
                          update papers set `exercise_num` = %s where `url` = %s
                       """

    def __init__(self, settings):
        self.settings = settings

    def process_item(self, item, spider):
        if spider.name == 'zujuan' or spider.name == 'zxls' or spider.name == 'gzzz':
            # 先判断试卷是否已经存在
            site_id = 202
            paper = item['paper']
            self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
            row = self.cursor.fetchone()
            print('===================')
            print('rowcount:%s' % self.cursor.rowcount)
            print('===================')
            if self.cursor.rowcount == 0:
                self.cursor.execute(self.paper_sql,
                                    (paper['title'],
                                     site_id,
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
        # elif spider.name == 'zxls':
        #     print('---存数据---')
        #     # 先判断试卷是否已经存在
        #     site_id = 203
        #     paper = item['paper']
        #     self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
        #     row = self.cursor.fetchone()
        #     print('===========')
        #     print('rowcount:%s' % self.cursor.rowcount)
        #     print('=========')
        #     if self.cursor.rowcount == 0:
        #         self.cursor.execute(self.paper_sql,
        #                             (paper['title'],
        #                              site_id,
        #                              paper['year'],
        #                              1,
        #                              paper['subject'],
        #                              paper['grade'],
        #                              paper['type'],
        #                              paper['exercise_num'],
        #                              paper['views'],
        #                              paper['uploaded_at'],
        #                              paper['url'])
        #                             )
        #         paper_id = self.cursor.lastrowid
        #     else:
        #         self.cursor.execute(self.paper_update_sql, (paper['exercise_num'], paper['url']))
        #         paper_id = row[0]
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
