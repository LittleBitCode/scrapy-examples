# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request , FormRequest
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from lxml import html
import json
from scrapy.http.cookies import CookieJar
import urllib
import time
import re
import random
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
# 实例化一个cookiejar对象
cookie_jar = CookieJar()

class ZxlsSpider(scrapy.Spider):
    name = 'zxls'
    allowed_domains = ['zujuan.zxls.com']
    start_urls = [
        'http://zujuan.zxls.com/',
        'http://zujuan.zxls.com/PaperLatest.aspx',
        'http://zujuan.zxls.com/PaperList.aspx?',
    ]
    base_url = 'http://zujuan.zxls.com'

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host":"zujuan.zxls.com",
        "Origin":"http://zujuan.zxls.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Referer": "http://zujuan.zxls.com/Index.aspx"
    }

    cid = {
        1 : '历史'
    }

    exercise_type = ''

    cookies = {
        'ASP.NET_SessionId':'4v4kzhdkqda3vp5dhedkb014',
        'kemu':'1'
    }
    # cookies = {}
    def start_requests(self):
        return [Request(self.base_url + '/Login.aspx?ReturnUrl=/Index.aspx',cookies={'kemu':'1'}, meta = {'cookiejar' : 1},callback = self.login)]

    def login(self,response):
        viewState           = Selector(response).xpath('//input[@name="__VIEWSTATE"]/@value').extract()[0]
        viewStateGenerator  = Selector(response).xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').extract()[0]
        eventValidation     = Selector(response).xpath('//input[@name="__EVENTVALIDATION"]/@value').extract()[0]
        captcha_img         = self.base_url + '/' + Selector(response).xpath("//img[@id='imgcode']/@src").extract()[0]
        localPath           = '/Users/zhengchaohua/Desktop/images/captcha.png'
        urllib.urlretrieve(captcha_img, localPath)
        # captcha_value       = raw_input('查看captcha.png,有验证码请输入:')
        formdata = {
                    '__VIEWSTATE'           : viewState,
                    '__VIEWSTATEGENERATOR'  : viewStateGenerator,
                    '__EVENTVALIDATION'     : eventValidation,
                    'txtUserName'           : 'dawnhome',
                    'txtPassword'           : 'mima0125',
                    'CheckBox1'             : 'on',
                    # 'ImageButton1.x'        : '136',
                    # 'ImageButton1.y'        : '30',
                    # 'txtYzmCode'            : captcha_value
                   }
        return [FormRequest.from_response(
            response,
            meta        = {'cookiejar': response.meta['cookiejar']},
            headers     = self.headers,
            formdata    = formdata,
            callback    = self.after_login
        )]


    def after_login(self,response):
        cookie_strings = response.request.headers.getlist('Cookie')[0]
        cookies = str(cookie_strings).split(';')
        cookie_dic = {}
        for cookie in cookies:
            key = cookie.split('=')[0].replace(' ', '')
            value = cookie.split('=')[1]
            cookie_dic[key] = value
        # self.cookies = cookie_dic
        print(self.cookies)
        yield FormRequest(
                self.base_url + '/Web/ashx_/PaperSearch.ashx',
                headers=self.headers,
                cookies=self.cookies,
                meta = {"cookiejar":response.meta["cookiejar"]},
                formdata = {
                            'cid' : '1',
                            'gr'  : '高三级',
                            'cty' : '高考真题',
                            'page': '1',
                            'rows': '10'
                           },
                callback = self.parse_paper_list,
                dont_filter=True
        )

    def parse_paper_list(self,response):
        js         = json.loads(response.body)
        xml_string = html.fromstring(js['data'])
        papers     = xml_string.xpath("//a[@class='goto']/@href")
        for index,paper in enumerate(papers):
            if 'PaperCenter' in paper:
                continue
            else:
                url  = self.base_url+ '/' + paper
                year = xml_string.xpath("//tr['index']/td[5]/text()")[index]
                yield Request(
                    url,
                    cookies  = self.cookies,
                    meta     = {'year':year,"cookiejar":response.meta["cookiejar"]},
                    callback = self.parse_exercise_list,
                    dont_filter=True
                )
        # 下一页
        page_string  = html.fromstring(js['pager'])
        current_page = page_string.xpath("//a[@class='change']/text()")[0]
        total_page   = int( int(js['total']) / 10) + 1
        next_page    = int(current_page) + 1
        if next_page <= total_page:
            yield FormRequest(
                self.base_url + '/Web/ashx_/PaperSearch.ashx',
                cookies  = self.cookies,
                headers  = self.headers,
                meta     = {"cookiejar": response.meta["cookiejar"]},
                formdata = {
                    'cid' : '1',
                    'gr'  : '高三级',
                    'cty' : '高考真题',
                    'page': str(next_page),
                    'rows': '10'
                },
                callback = self.parse_paper_list,
                dont_filter=True
            )

    def parse_exercise_list(self, response):
        url          = response.url
        title        = response.xpath("//div[@class='sjbt']/h1/text()").extract_first()
        subject      = self.cid[1]
        grade        = response.xpath("//div[@class='xiaobiaoti']/span[1]/text()").extract_first().replace(u'适用年级：' , '')
        type         = response.xpath("//div[@class='xiaobiaoti']/span[2]/text()").extract_first().replace(u'试卷类型：' , '')
        year         = response.xpath("//div[@class='xiaobiaoti']/span[4]/text()").extract_first().replace(u'试卷年份：' , '').replace(u'年','')
        exercise_num = response.xpath("//div[@class='xiaobiaoti']/span[5]/text()").extract_first().replace(u'题数：'    , '')
        views        = response.xpath("//div[@class='xiaobiaoti']/span[6]/text()").extract_first().replace(u'浏览数：'  , '')
        uploaded_at  = response.meta['year']
        paper = {
            'url'           : url,
            'title'         : title,
            'subject'       : subject,
            'grade'         : grade,
            'type'          : type,
            'level'         : '1',
            'year'          : year,
            'views'         : views,
            'exercise_num'  : exercise_num,
            'uploaded_at'   : uploaded_at,
        }
        soup = BeautifulSoup(response.body,'lxml')
        sort = 0
        for child in soup.find('div',id='subjectList').contents:
            if child.name == None:
                continue
            # if child.name == 'p':
                # self.exercise_type = str(child.string).split('、')[-1]
            if child.name == 'div':
                tds         = child.find_all('td')
                description = str(tds[1])
                # imgs = child.find_all('img')
                # if len(imgs) > 0:
                #     for img in imgs:
                #         img_url = self.base_url+'/'+img['src']
                #         print(img_url)

                options     = child.find_all('td',attrs={'class':'sstd'})
                options_string = {}
                if len(options) > 0:
                    exercise_type = '单选题'
                else:
                    exercise_type = '材料阅读'
                for index,option in enumerate(options):
                    string = chr(ord(str(int(index))) + 17)
                    options_string[string] = str(option).split('．')[-1]
                options   = json.dumps(options_string)
                source_id = child.find_all('input')[0]['value']
                sort += 1
                exercise = {
                    'subject'      : subject,
                    'degree'       : None,
                    'source_id'    : source_id,
                    'type'         : exercise_type,
                    'description'  : description,
                    'options'      : options,
                    'answer'       : None,
                    'method'       : None,
                    'points'       : None,
                    'url'          : None,
                    'sort'         : sort,
                    'paper'        : paper
                }
                yield Request(
                        self.base_url+'/Web/ashx_/ProblemAttend.ashx?id=' + source_id,
                        cookies  = self.cookies,
                        meta     = {'exercise':exercise,"cookiejar":response.meta["cookiejar"]},
                        callback = self.parse_exercise_detail
                    )

    def parse_exercise_detail(self,response):
        exercise   = response.meta['exercise']
        js         = json.loads(response.body)
        xml_string = html.fromstring(js['data'])
        points     = str(xml_string.xpath("//p[3]/text()")[0]).split('】')[-1].split('；')
        points_dics= {}
        for index,point in enumerate(points):
            points_dics[index] = point
        points     = json.dumps(points_dics)
        method     = str(xml_string.xpath("//p[6]/text()")[0])
        answer     = str(xml_string.xpath("//p[7]/text()")[0]).split('】')[-1]
        degree     = str(xml_string.xpath("//p[last()-2]/text()")[0]).split('】')[-1]
        yield {
            'subject'       : exercise['subject'],
            'degree'        : degree,
            'source_id'     : exercise['source_id'],
            'type'          : exercise['type'],
            'description'   : exercise['description'],
            'options'       : exercise['options'],
            'answer'        : answer,
            'method'        : method,
            'points'        : points,
            'url'           : 'url',
            'sort'          : exercise['sort'],
            'paper'         : exercise['paper']
        }

