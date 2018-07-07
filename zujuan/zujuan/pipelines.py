# pipelines.py
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import logging
import json


class ZujuanPipeline(object):
    paper_sql = """
                   insert into papers(`title`   ,`site_id` ,`year` ,`level`        ,
                                      `subject` ,`grade`   ,`type` ,`exercise_num` ,
                                      `views`,`uploaded_at`,`url`
                                      )
                         values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
    zxls_paper_sql = """
                   insert into papers(`title`   
                                      )
                         values(%s)
                """

    exercise_sql = """
                      insert into exercises( `subject`  ,`type`        , `degree`    ,`source_id`,
                                             `paper_id` ,`description` ,`method_img` ,`answer_img`,
                                             `options`  ,`points`      ,`url`        ,`sort`
                                            )
                             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
    paper_update_sql = """
                          update papers set `exercise_num` = %s where `url` = %s
                       """

    def __init__(self, settings):
        self.settings = settings
        # reload(sys)  # 2
        # sys.setdefaultencoding('utf-8')

    def process_item(self, item, spider):
        if spider.name == 'zujuan':
            # 先判断试卷是否已经存在
            site_id = 202
            paper = item['paper']
            self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
            row = self.cursor.fetchone()
            print('===========')
            print('rowcount:%s' % self.cursor.rowcount)
            print('=========')
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
                self.cursor.execute(self.paper_update_sql,(paper['exercise_num'],paper['url']))
                paper_id = row[0]

            print(">>>>>>>>>>>>>> new paper id: %s" % (paper_id))
            # 写入试题表
            self.cursor.execute(self.exercise_sql, (
                    item['subject'],
                    item['type'],
                    item['degree'],
                    item['source_id'],
                    paper_id,
                    pymysql.escape_string(item['description']),
                    pymysql.escape_string(item['method']),
                    pymysql.escape_string(item['answer']),
                    item['options'],
                    item['points'],
                    item['url'],
                    item['sort']
                )
            )
        elif spider.name == 'zxls':
            print('---存数据---')
            # 先判断试卷是否已经存在
            site_id = 203
            paper = item
            self.cursor.execute(self.zxls_paper_sql,
                                paper['title'])
            paper_id = self.cursor.lastrowid
        else:
            spider.log('Undefined name: %s' % spider.name)

        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):
        # 连接数据库
        self.connect = pymysql.connect(
            host=self.settings.get('MYSQL_HOST'),
            port=self.settings.get('MYSQL_PORT'),
            db=self.settings.get('MYSQL_DBNAME'),
            user=self.settings.get('MYSQL_USER'),
            passwd=self.settings.get('MYSQL_PASSWD'),
            charset='utf8',
            use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor()
        self.cursor.execute('SET NAMES utf8')
        self.cursor.execute('SET CHARACTER SET utf8')
        self.cursor.execute('SET CHARACTER_SET_CONNECTION=utf8')
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
