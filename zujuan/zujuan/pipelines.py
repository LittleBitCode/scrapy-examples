# pipelines.py
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import json
import time
import redis
import pymysql
import zujuan.settings       as set

from aip                     import AipOcr
from scrapy                  import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions       import DropItem
from zujuan.items            import ImageItem
from zujuan.items            import ExerciseItem

local_redis = redis.Redis(host='127.0.0.1',port=6379)
# 下载图片
class DownloadImagesPipeline(ImagesPipeline):
    first_folder = {
        '8': 'zujuan_21cnjy',
        '13': 'zxls'
    }
    # 1. 下载图片
    def get_media_requests(self, item, info):
        if item['answer_img'] != None or item['answer_img'] != '' :
            image_urls = {
                'answer': item['answer_img'],
            }
            for key in dict(image_urls).keys():
                if image_urls[key] != None and str(image_urls[key]).startswith('http'):
                    print('-------------  开始下载图片%s -----------' % ( image_urls[key]))
                    yield Request(
                        image_urls[key],
                        meta={
                            'item'  : item,
                            'key'   : key,
                            'index' :'1'
                        }
                    )  # 添加meta是为了下面重命名文件名使用
        if item['method_img'] != None or item['method_img'] != '':
            image_urls = {
                'method': item['method_img']
            }
            for key in dict(image_urls).keys():
                if image_urls[key] != None and str(image_urls[key]).startswith('http'):
                    print('-------------  开始下载图片%s -----------' % ( image_urls[key]))
                    yield Request(
                        image_urls[key],
                        meta={
                            'item'  : item,
                            'key'   : key,
                            'index' :'1'
                        }
                    )  # 添加meta是为了下面重命名文件名使用
        if item['description_imgs'] != None:
            image_urls = dict(item['description_imgs'])
            index = 0
            for key in image_urls.keys():
                if image_urls[key] != None and str(image_urls[key]).startswith('http'):
                    index+=1
                    print('-------------  开始下载描述图片%s -----------' % (image_urls[key]))
                    yield Request(
                        image_urls[key],
                        meta={
                            'item' : item,
                            'key'  : 'description',
                            'index': str(index)
                        }
                    )  # 添加meta是为了下面重命名文件名使用
    # 2. 重写保存图片路径方法
    def file_path(self, request, response=None, info=None):
        item        = request.meta['item']
        firstFolder = request.meta['key']
        image_guid  = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        name        = item['source_id'] + '_' + request.meta['index']
        ext         = str(request.url.split('/')[-1].split('.')[-1]).split('?')[0]
        image_name  = name + '.' + ext
        key         = str(item['site_id'])
        filename    = u'{0}/{1}/{2}'.format(self.first_folder[key],firstFolder, image_name)
        return filename
    # 3. 图片下载完成
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]  # ok判断是否下载成功
        if not image_paths:
            return item
        else:
            for image_path in image_paths:
                folder = str(image_path).split('/')[1]
                if folder == 'answer':
                    item['answer_img'] = image_path
                elif folder == 'method':
                    item['method_img'] = image_path
                elif folder == 'description':
                    image_urls = item['description_imgs']
                    if len(dict(image_urls).keys()) > 0:
                        image_list = list(dict(image_urls).keys())
                        for index,key in enumerate(image_list):
                            image_path_index = str(image_path).split('_')[-1].split('.')[0]
                            if int(image_path_index) == int(index)+1:
                                descrption = str(item['description'])
                                new_descrption = descrption.replace(key,image_path)
                                item['description'] = new_descrption
            print('------------ 图片下载完成 %s ------------' % image_paths)
            return item

#图片识别
class ocrPipeline(object):
    def __init__(self, settings):
        self.settings = settings

    index   = int(local_redis['account_index'])
    if index == None:
        index = 0

    account = [
        # {
        #     'APP_ID': '11501062',
        #     'API_KEY': 'Ld7fqNs8GsXoxVIpuYHALEw0',
        #     'SECRET_KEY': 'mrMI4s7Bce0focebXGOzGq3lah80e9bM',
        # },
        # {
        #     'APP_ID': '11497928',
        #     'API_KEY': 'koU2CIiT3ux3QCIiP8YiYPGT',
        #     'SECRET_KEY': 'KmhsSPSrXuwuQUjboqpct0HLqPebS0eD',
        # },
        # {
        #     'APP_ID': '11501079',
        #     'API_KEY': 'GRoaofnAbOMN1oVDC52cQz0m',
        #     'SECRET_KEY': '4YOT2ZhsOi7ZdrEATWxqqS0Gi0HyzNhA',
        # },
        # {
        #     'APP_ID': '11498211',
        #     'API_KEY': 'pyeYqt5lvjgD9S9zoCXijB3I',
        #     'SECRET_KEY': 'zweInf76lzg3DmyO7IwMb2LMcqkcaRPg',
        # },
        # {
        #     'APP_ID': '11512121',
        #     'API_KEY': 'PRV5tl7yZ2gRA4jEbhNpgniD',
        #     'SECRET_KEY': 'aeCD2G7G86Q3tcmwMSbGwPGQAAUdesQR',
        # },
        # {
        #     'APP_ID': '11499017',
        #     'API_KEY': 'M35qyyCuhLefaWxZ3NOxH9aI',
        #     'SECRET_KEY': 'ABICflGZvTjAZk5oo7zao9lkApFFXjYl ',
        # },
        # {
        #     'APP_ID': '11511983',
        #     'API_KEY': 'M1yPkl8yXtrKnzzmkPvEu6xo',
        #     'SECRET_KEY': 'QQYpsdYSiLowQL2nDzjNKEhkSCk1VD8S ',
        # },
        # {
        #     'APP_ID': '11512150',
        #     'API_KEY': 'Qc1WLaVbCiwbmb29r7qv9gMg',
        #     'SECRET_KEY': '1RMRbAXyBF9tbr5EkfgK13xNSG7wzEcU',
        # },
        # {
        #     'APP_ID': '11501055',
        #     'API_KEY': 'BxdLhSO0kavN79IKjH7z2g6r',
        #     'SECRET_KEY': '6V3IkrG5qwScDphGmLUvBwFSO46Z9Sfh',
        # },
        # {
        #     'APP_ID': '11512526',
        #     'API_KEY': '4m6L6GeUUGOQHaRCkB4ZVC9x',
        #     'SECRET_KEY': 'Uv1bS8KZ8sSdipq7SxZYQ61ZOvYSCodz',
        # },
        # {
        #     'APP_ID': '11501223',
        #     'API_KEY': 'v2WRrnNmmXo7TL1hZE5jYyNy',
        #     'SECRET_KEY': 'SHIbW69rcE5tD1PW0xLIiDIg5hRF9F5s ',
        # },
        # {
        #     'APP_ID': '11511997',
        #     'API_KEY': 'vHBhHHuxfdqKrrL3h40nIumZ',
        #     'SECRET_KEY': 'xPMWuNydtMPGA2rnqjdg4dGrUdujy3ki ',
        # },
        # {
        #     'APP_ID': '11508592',
        #     'API_KEY': 'YyWYF7hdm6bUhPMj3VB22skH',
        #     'SECRET_KEY': 'DMqMGW6YSiYqvX7kKAQBe80QGXUf5bfD',
        # },
        # {
        #     'APP_ID': '11509557',
        #     'API_KEY': 'E2fD8p7ZUT54ZPcEZIS3Cgwu',
        #     'SECRET_KEY': 'IdGRmLMWm5nQ1F8IZsV3IPa5zHEgkDXT',
        # },
        # {
        #     'APP_ID': '11501507',
        #     'API_KEY': 'O8GZeDj0dY8dTdp9m5B9sN45',
        #     'SECRET_KEY': 'GoGiMBG5Gyk2M24HG45avDEEZWbK19pq',
        # },
        # {
        #     'APP_ID': '11501147',
        #     'API_KEY': '4ZvN88EFEMb3up40H6e33AqB',
        #     'SECRET_KEY': 'gE1oBNxaExbMn2emHWFQQcV9zgHBlngk',
        # },
        # {
        #     'APP_ID': '11511920',
        #     'API_KEY': 'GHYNs8fEbkAQz1tOFfUW0YDs',
        #     'SECRET_KEY': 'xdoLyOHNhMwaNejpuikmNPLGk8jxxToK',
        # },
        # {
        #     'APP_ID': '11511917',
        #     'API_KEY': 'seaw1cHy1gzmwzWGSzwPpW3B',
        #     'SECRET_KEY': 'GHGDuorgwComGSo9O06FKA9S5jsEiOhI',
        # },
        # {
        #     'APP_ID': '11501052',
        #     'API_KEY': '9ZshmGRb3hgrMLBbd8hGnnbt',
        #     'SECRET_KEY': 'MAQyRO7G7oDB2oXX8ewE7AhrVLonUN2f',
        # },
        # {
        #     'APP_ID': '11508393',
        #     'API_KEY': 'gdS8oFrm0S7gWGsV4Oj6fSGG',
        #     'SECRET_KEY': 'Is1QLt82O3QtBEkFHdfz1ScFSsnbkIqU',
        # },
        # {
        #     'APP_ID': '11508446',
        #     'API_KEY': '89TjuhYytRfjwsOoGmTtc12n',
        #     'SECRET_KEY': 'GVsifWWvZ6gs0B3a84dnT2siyoabMhbw',
        # },
        # {
        #     'APP_ID': '11508422',
        #     'API_KEY': 'IPXIjqzhyGwSSGfAKb7Z2UD2',
        #     'SECRET_KEY': 'qTSlgU6FGkCRGPW3QyLXVGwon0rGZ3xq',
        # },
        # {
        #     'APP_ID': '11501314',
        #     'API_KEY': 'ECt06scGz3dD62C7gzOiGI0Z',
        #     'SECRET_KEY': 'iPQsYRXsuogw4UXy0du8G3iIWAkQ7rgn',
        # },
        # {
        #     'APP_ID': '11501102',
        #     'API_KEY': 'sYgaklfenTbYRbijTQd7VCrL',
        #     'SECRET_KEY': 'r2y5t4kwMbr0l34DPtW11cSGnwBZIqZz',
        # },
        # {
        #     'APP_ID': '11512409',
        #     'API_KEY': 'bED2Md2eKOGxdvO8xfBOgGs5',
        #     'SECRET_KEY': 'NT3kH8BEKoWNwD975PXbsDyYd7vIuGcx',
        # },
        # {
        #     'APP_ID': '11508688',
        #     'API_KEY': '7LgL3pMmb3r5qTfPZzUhh0D0',
        #     'SECRET_KEY': '3t20BgAG6i4WmQM5eowGHPIVFSShOG8s',
        # },
        # {
        #     'APP_ID': '11501503',
        #     'API_KEY': 'I2nB2LG3yzNBCi1Ur62oFkWG',
        #     'SECRET_KEY': 'yAhClsv2Q0uFigvGy5wFgbdStWfIVwi6 ',
        # },
        # {
        #     'APP_ID': '11512103',
        #     'API_KEY': 'g75Gu4OOvpzfm2HOjVAnGHBC',
        #     'SECRET_KEY': 'gEUczb8cDdjKAulMbKXi92mtDHSkP1kl',
        # },
        # {
        #     'APP_ID': '11501067',
        #     'API_KEY': 'GmbzOe92OEEFRKV0bEUuhHZr',
        #     'SECRET_KEY': 'wjLcpTFG5j5XdVMv00KzEd8VSjxCQX3x',
        # },
        # {
        #     'APP_ID': '11501440',
        #     'API_KEY': 'eNRf3zqGGEnL6oyW8ZV5QcC5',
        #     'SECRET_KEY': 'A1Gb80mfb5uRMBVZZbK0lRBrlIqyNk4V ',
        # },
        # {
        #     'APP_ID': '11508385',
        #     'API_KEY': 'UV8M1PeLsWLgVlxzyMugbivd',
        #     'SECRET_KEY': 'ql9WTbRLhNMd6BnVRA2SwSjeFZaccYPx',
        # },
        # {
        #     'APP_ID': '11512350',
        #     'API_KEY': 'hAEesA4XVTaTwWyWqEBmcs71',
        #     'SECRET_KEY': 'x2IzDNpLoZmDSlxOHZEw2VDMGzdzbOcK',
        # },
        # {
        #     'APP_ID': '11512200',
        #     'API_KEY': 'c2HcHapOALHaMNVIjuIaXd7v',
        #     'SECRET_KEY': 'nKn5TYdw3ollXBZqeco9sULyfFToSijq',
        # },
        # {
        #     'APP_ID': '11512360',
        #     'API_KEY': 'FE9A7HWZiEDvqjqFsDvFsBeZ',
        #     'SECRET_KEY': 'wSpOhTN3HSAXK1gcoOKYBmqEOBsRGMTl ',
        # },
        # {
        #     'APP_ID': '11512349',
        #     'API_KEY': 'mWMtly0CSTzo3pK3bRSA5Yxq',
        #     'SECRET_KEY': 'sttyTYNF9cltzkKFfSUfgFgwxoRsYZGI ',
        # },
        # {
        #     'APP_ID': '11512259',
        #     'API_KEY': '4GjeW7PC6VFeYkde3Oy4olq5',
        #     'SECRET_KEY': 'AHHv0KNr3rbMpcXA0xW8HBndMsyFTuYD',
        # },
        # {
        #     'APP_ID': '11512550',
        #     'API_KEY': 'hs0t6EGmtQoDE7CL1OjBChSi',
        #     'SECRET_KEY': 'fHfvNRxQBODFAdgvQBeIAbKQcP0e7997',
        # },
        # {
        #     'APP_ID': '11501189',
        #     'API_KEY': 'ZfvdMWiUcfx0S8SecSn6n7Et',
        #     'SECRET_KEY': 'R5yLerh139EYYBLA4yl0qQ9kGKcywsw9',
        # },
        # {
        #     'APP_ID': '11501058',
        #     'API_KEY': 'SCcdnRmpdaspVbGVPnMT0iCA',
        #     'SECRET_KEY': 'p8hGQEOgkacuTH09VFEVC0EtBDuIhtHU',
        # },
        # {
        #     'APP_ID': '11512011',
        #     'API_KEY': 'A4bkwbvAaT9mcBj1lT3WV7On',
        #     'SECRET_KEY': '8Z4Sy1UZe6oqARkToZrtFCoQfjD7BGos',
        # },
        # {
        #     'APP_ID': '11508450',
        #     'API_KEY': '0uGsmW6lYE1AOlwoRTT4o680',
        #     'SECRET_KEY': '0eIhRqSFByPm2ZY19gwv3pn9QnKxxIsZ',
        # },
        # {
        #     'APP_ID': '11501198',
        #     'API_KEY': 'Ghs8LR9jiKsTYuTcnSvXVdrB',
        #     'SECRET_KEY': 'TIn8gkvBC0cstf0WkgGr3FsSvu2SMsPy',
        # },
        # {
        #     'APP_ID': '11512034',
        #     'API_KEY': 'W0MYADsPCg4vNIbWoYktRqL2',
        #     'SECRET_KEY': 'bFUatDIs7oTsxjeg2x9L2RGqu4mkLVv9',
        # },
        # {
        #     'APP_ID': '11514697',
        #     'API_KEY': 'lKHrWl32xzpTh4HClvQxxmxi',
        #     'SECRET_KEY': 'e8b1SMazyKBhY5rIb6p0qeHsrCcXPaUR',
        # },
        # {
        #     'APP_ID': '11542143',
        #     'API_KEY': 'QmBc3mArK9cf267zGPrAxVNG',
        #     'SECRET_KEY': 'Hn9IkTVAD1DHQHf9Ew2VNatVrGMWXgEe',
        # },
        {
            'APP_ID': '11532440',
            'API_KEY': 'hhW4gM2CAZdsUqjUyIA1WxZF',
            'SECRET_KEY': 'Thh51ejbCG4u1eV1CUWa6WYW7blsrsX5',
        },
        {
            'APP_ID': '10733367',
            'API_KEY': 'WYAFwtoMQoapxd4poaDm7hB2',
            'SECRET_KEY': 'AGBBRZ8QKGrN1vaMeDosHlLWY7GaqzNA',
        },
        {
            'APP_ID': '10710943',
            'API_KEY': '2EDYpfWbnSsSBhGHBCA1DK1k',
            'SECRET_KEY': 'rdMt7adACFmRQWKzF8lGCCRT8h2NDqQx',
        },
        {
            'APP_ID': '10784818',
            'API_KEY': 'G7T90DoNG1AGj8eUOdkLHIuR',
            'SECRET_KEY': 'iHUyLs70PqKCGGnpG6PG8U7iUvPpD1n0',
        },
        {
            'APP_ID': '10788064',
            'API_KEY': 'XTjqKzNRUzrIZvWkOGN31gPu',
            'SECRET_KEY': 'dQZj5bywzHcm1QtSEBMUqp85VXDp0CQc',
        },
        {
            'APP_ID': '10797268',
            'API_KEY': 'tku0zN0nyo4rV1GlFDYBqgBI',
            'SECRET_KEY': 'TGPmVlGgCKfig6o4HIxV3Q79C8kquzpz',
        },
        {
            'APP_ID': '10797257',
            'API_KEY': 'I4v4mUbkV5pwSgfUIqZ9DUBz',
            'SECRET_KEY': 'TahfDuzFo26n7Q7pMk1fhdVh3fGQteat',
        },
        {
            'APP_ID': '10733367',
            'API_KEY': 'WYAFwtoMQoapxd4poaDm7hB2',
            'SECRET_KEY': 'AGBBRZ8QKGrN1vaMeDosHlLWY7Gaqz',
        },
    ]
    current_account = account[index]

    def get_file_content(self,filePath):
        with open(filePath,'rb') as fp:
            return fp.read()

    def ocrImage(self,path,account):
        client = AipOcr(account['APP_ID'], account['API_KEY'], account['SECRET_KEY'])
        result_words = ''
        if str(path).startswith('http'):
            result = client.basicGeneralUrl(path)
            result = dict(result)
        elif str(path).find('http') > 0:
            return ''
        else:
            image = self.get_file_content(path)
            result = client.basicGeneral(image)
            # result = client.basicAccurate(image)#高精度识别
            result = dict(result)

        if result.has_key('error_msg'):
            try:
                self.changeBaiduAccount(path=path)
            except Exception as e:
                print('--------------------------------')
                print(e.message)
                print('--------------------------------')
                return ''
        else:
            if int(result['words_result_num']) > 0:
                for words in result['words_result']:
                    result_words += words['words']
        return result_words

    def changeBaiduAccount(self,path):
        length = len(self.account)
        account_index = int(local_redis['account_index'])
        index = 0
        if account_index +1 >= length:
            local_redis.set('account_index', 0)
            cycle_num = int(local_redis['cycle_num'])
            if cycle_num < 2:
                local_redis.set('cycle_num',cycle_num + 1)
            else:
                local_redis.set('cycle_num',0)
                raise Exception("没有可以使用的账号 %s %s %s" % (
                    self.account[account_index]['APP_ID'],
                    self.account[account_index]['API_KEY'],
                    self.account[account_index]['SECRET_KEY'])
                )
        else:
            local_redis.set('account_index',account_index + 1)
            index = account_index + 1
        self.ocrImage(path=path, account=self.account[index])

    def process_item(self, item, spider):
        if spider.name == 'zujuan' or spider.name == 'c_e':
            result_words = ''
            #1.判断数据表中是否存在
            self.cursor.execute("select id from exercises where site_id='%s' and source_id = '%s'" % (item['site_id'],item['source_id']))
            row = self.cursor.fetchone()
            rootPath = str(set.project_dir)
            if item['method_img'] != None and item['method_img'] != '':
                filePath = "%s/%s" % (rootPath, item['method_img'])
                if row:  # 如果数据表中有该条数据
                    self.cursor.execute("select * from exercises where id='%s'" % (row[0]))
                    result = self.cursor.fetchone() #取出该条数据
                    if result[10] == None:  # 判断数据表中该字段是否为空值
                        result_words = self.ocrImage(filePath,self.current_account)
                else:   # 如果表中没有此条数据
                    result_words = self.ocrImage(filePath,self.current_account)
                if result_words == '':
                    item['method'] = None
                else:
                    item['method'] = result_words
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            if item['answer_img'] != None and item['answer_img'] != '':
                filePath = "%s/%s" % (rootPath,item['answer_img'])
                if row:  # 如果数据表中有该条数据
                    self.cursor.execute("select * from exercises where id='%s'" % (row[0]))
                    result = self.cursor.fetchone() #取出该条数据
                    if result[13] == None:  # 判断数据表中该字段是否为空值
                        result_words = self.ocrImage(filePath,self.current_account)
                else:   # 如果表中没有此条数据
                    result_words = self.ocrImage(filePath,self.current_account)
                if result_words == '':
                    item['answer'] = None
                else:
                    item['answer'] = result_words
                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
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
            use_unicode=True
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

class ZujuanPipeline(object):
    # 试卷
    paper_sql = """
                   insert into papers(
                   `title` ,`site_id` ,`year`         ,`level` ,`subject`     ,
                   `grade` ,`type`    ,`exercise_num` ,`views` ,`uploaded_at` ,
                   `url`
                   )values(
                   %s,%s,%s,%s,%s,
                   %s,%s,%s,%s,%s,
                   %s)
                """
    #习题
    exercise_sql = """
                      insert into exercises(
                      `subject`  ,`grade`      ,`type`        ,`degree` ,`source_id`  ,
                      `paper_id` ,`site_id`    ,`description` ,`method` ,`method_img` ,
                      `answer`   ,`answer_img` ,`options`     ,`points` ,`url`        ,
                      `is_wrong` ,`sort`
                      ) values( 
                      %s,%s,%s,%s,%s,
                      %s,%s,%s,%s,%s,
                      %s,%s,%s,%s,%s,
                      %s,%s)
                   """
    # 学段 （小学 初中 高中...）
    section_sql  = """
                        insert into sections(
                        `name`,`site_id`
                        ) values (
                        %s,%s)
                    """
    # 学科 （语文 数学 ...）
    subject_sql = """
                      insert into subjects(
                      `name`,`site_id`,`section_id`
                      ) values (
                      %s,%s,%s)
                 """
    # 版本 （人教版 部编版 ...）
    edition_sql = """
                        insert into editions(
                        `id`,`name`,`subject_id`,`site_id`,`section_id`
                        ) values (
                        %s,%s,%s,%s,%s)
                    """
    # 年级 （七年级上册 七年级下册 ...）
    textbook_sql = """
                        insert into textbooks(
                        `name`,`source_id`,`edition`,`edition_id`,`site_id`,
                        `grade`,`subject`,`term`
                        ) values (
                        %s,%s,%s,%s,%s,
                        %s,%s,%s)
                    """
    # 章节 （第一单元 第二单元 有理数 无理数 ...）
    chapter_sql = """
                        insert into chapters(
                        `name`  ,`parent_id` ,`source_id` ,`edition`     ,`edition_id`  ,
                        `grade` ,`subject`   ,`textbook`  ,`textbook_id` ,`have_child`
                        ) values (
                        %s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s)
                    """
    # 章节对应的试卷
    chapter_paper_sql = """
                        insert into chapter_paper(
                        `chapter_id`,`paper_id`
                        )values (
                        %s,%s)
                        """
    # 习题对应的试卷
    exercise_paper_sql = """
                        insert into exercise_paper(
                        `exercise_id`,`paper_id`
                        )values (
                        %s,%s)
                        """
    #更新试卷习题数量
    paper_update_exercise_num_sql = """
                                    update papers set `exercise_num` = %s where `url` = %s
                                    """
    # 图片识别后 更新试题解析
    exercise_update_method_sql = """
                                    update exercises set `method` = %s where `url` = %s
                                 """
    # 图片识别后 更新试题答案
    exercise_update_answer_sql = """
                                    update exercises set `answer` = %s where `url` = %s
                                 """

    def __init__(self, settings):
        self.settings = settings

    def process_item(self, item, spider):
        if spider.name == 'zujuan' or spider.name == 'zxls':
            # 先判断试卷是否已经存在
            paper = item['paper']
            self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
            row = self.cursor.fetchone()
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
                    self.cursor.execute(self.paper_update_exercise_num_sql,(paper['exercise_num'],paper['url']))
                paper_id = row[0]

            print(">>>>>>>>>>>>>>>>>>>>>>>> new paper id: %s <<<<<<<<<<<<<<<<<<<<<<<<" % (paper_id))
            self.cursor.execute("select id from exercises where site_id='%s' and source_id = '%s'" % (item['site_id'],item['source_id']))
            row = self.cursor.fetchone()
            if row :
                self.cursor.execute("select * from exercises where id='%s'" % (row[0]))
                result = self.cursor.fetchone()
                if result[10] == None:
                    if item['method'] != None:
                        self.cursor.execute(self.exercise_update_method_sql,(
                                item['method'],
                                item['url']
                            ))
                if result[13] == None:
                    if item['answer'] != None:
                        self.cursor.execute(self.exercise_update_answer_sql, (
                            item['answer'],
                            item['url']
                        ))
            else:   # 写入试题表
                self.cursor.execute(self.exercise_sql, (
                        item['subject'],
                        item['grade'],
                        item['type'],
                        item['degree'],
                        item['source_id'],
                        paper_id,
                        item['site_id'],
                        item['description'],
                        item['method'],
                        item['method_img'],
                        item['answer'],
                        item['answer_img'],
                        item['options'],
                        item['points'],
                        item['url'],
                        item['is_wrong'],
                        item['sort']
                    )
                )
        elif spider.name == 'c_e':
            paper = item['paper']
            self.cursor.execute("select id from papers where url='%s'" % (paper['url']))
            row = self.cursor.fetchone()
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
                self.cursor.execute(self.paper_update_exercise_num_sql, (paper['exercise_num'], paper['url']))
                paper_id = row[0]
            # 1. section
            section = item['section']
            self.cursor.execute("select id from sections where site_id='%s' and name='%s'" %(item['site_id'],section['name']))
            row = self.cursor.fetchone()
            if row:
                section_id = row[0]
            else:
                self.cursor.execute(self.section_sql,(
                    section['name'],
                    item['site_id']
                ))
                section_id = self.cursor.lastrowid
            # 2. subject
            subject = item['subjects']
            self.cursor.execute("select id from subjects where site_id='%s' and name='%s'" %(item['site_id'],subject['name']))
            row = self.cursor.fetchone()
            if row:
                subject_id = row[0]
            else:
                self.cursor.execute(self.subject_sql, (
                    subject['name'],
                    item['site_id'],
                    section_id
                ))
                subject_id = self.cursor.lastrowid
            # 3. edition
            chapter = item['chapter']
            self.cursor.execute(
                "select id from editions where site_id='%s' and name='%s'" % (item['site_id'], chapter['edition']))
            row = self.cursor.fetchone()
            if row:
                edition_id = chapter['edition_id']
            else:
                self.cursor.execute(self.edition_sql, (
                    chapter['edition_id'],
                    chapter['edition'],
                    subject_id,
                    item['site_id'],
                    section_id
                ))
                edition_id = chapter['edition_id']
            # 4. textbook
            chapter = item['chapter']
            self.cursor.execute(
                "select id from textbooks where site_id='%s' and name='%s'" % (item['site_id'], chapter['textbook']))
            row = self.cursor.fetchone()
            if row:
                textbook_id = row[0]
            else:
                self.cursor.execute(self.textbook_sql, (
                    chapter['textbook'],
                    chapter['textbook_id'],
                    chapter['edition'],
                    edition_id,
                    item['site_id'],
                    item['grade'],
                    item['subject'],
                    item['term'],
                ))
                textbook_id = self.cursor.lastrowid
            # 5. unit
            chapter = item['unit']
            self.cursor.execute(
                "select id from chapters where source_id='%s' and name='%s'" % (chapter['id'], chapter['name']))
            row = self.cursor.fetchone()
            if row:
                unit_id = row[0]
            else:
                self.cursor.execute(self.chapter_sql, (
                    chapter['name'],
                    chapter['parent_id'],
                    chapter['id'],
                    chapter['edition'],
                    edition_id,
                    item['grade'],
                    item['subject'],
                    chapter['textbook'],
                    textbook_id,
                    chapter['have_child']
                ))
                unit_id = self.cursor.lastrowid
            # 5. chapter
            chapter = item['chapter']
            self.cursor.execute(
                "select id from chapters where source_id='%s' and name='%s'" % (chapter['id'], chapter['name']))
            row = self.cursor.fetchone()
            if row:
                chapter_id = row[0]
            else:
                self.cursor.execute(self.chapter_sql, (
                    chapter['name'],
                    unit_id,
                    chapter['id'],
                    chapter['edition'],
                    edition_id,
                    item['grade'],
                    item['subject'],
                    chapter['textbook'],
                    textbook_id,
                    chapter['have_child']
                ))
                chapter_id = self.cursor.lastrowid


            # 6. chapter_paper
            self.cursor.execute("select * from chapter_paper where chapter_id='%s' and paper_id='%s'" % (chapter_id,paper_id))
            row = self.cursor.fetchone()
            if row:
                pass
            else:
                self.cursor.execute(self.chapter_paper_sql,(
                    chapter_id,
                    paper_id
                ))
            # 7. 习题
            self.cursor.execute("select id from exercises where site_id='%s' and source_id = '%s'" % (
            item['site_id'], item['source_id']))
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute("select * from exercises where id='%s'" % (row[0]))
                result = self.cursor.fetchone()
                if result[10] == None:
                    if item['method'] != None:
                        self.cursor.execute(self.exercise_update_method_sql, (
                            item['method'],
                            item['url']
                        ))
                if result[13] == None:
                    if item['answer'] != None:
                        self.cursor.execute(self.exercise_update_answer_sql, (
                            item['answer'],
                            item['url']
                        ))
                exercise_id = row[0]
            else:  # 写入试题表
                self.cursor.execute(self.exercise_sql, (
                    item['subject'],
                    item['grade'],
                    item['type'],
                    item['degree'],
                    item['source_id'],
                    paper_id,
                    item['site_id'],
                    item['description'],
                    item['method'],
                    item['method_img'],
                    item['answer'],
                    item['answer_img'],
                    item['options'],
                    item['points'],
                    item['url'],
                    item['is_wrong'],
                    item['sort']
                ))
                exercise_id = self.cursor.lastrowid
            # 8. 习题对应试卷
            self.cursor.execute("select * from exercise_paper where exercise_id='%s' and paper_id='%s'" % (exercise_id, paper_id))
            row = self.cursor.fetchone()
            if row:
                pass
            else:
                self.cursor.execute(self.exercise_paper_sql, (
                    exercise_id,
                    paper_id
                ))
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
