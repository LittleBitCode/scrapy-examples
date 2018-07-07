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
import re
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
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host":"zujuan.zxls.com",
        "Origin":"http://zujuan.zxls.com",
        "Cookie":"ASP.NET_SessionId=c54fr0tqccbfvxkuyrss3jjy; kemu=1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Referer": "http://zujuan.zxls.com/Login.aspx?ReturnUrl=%2fIndex.aspx"
    }

    def start_requests(self):
        url = self.base_url + '/Login.aspx?ReturnUrl=/Index.aspx'
        return [Request(url, meta = {'cookiejar' : 1},callback = self.login)]

    def login(self,response):
        viewState           = Selector(response).xpath('//input[@name="__VIEWSTATE"]/@value').extract()[0]
        viewStateGenerator  = Selector(response).xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').extract()[0]
        eventValidation = Selector(response).xpath('//input[@name="__EVENTVALIDATION"]/@value').extract()[0]
        captcha_img = 'http://zujuan.zxls.com/CheckCode.aspx'
        localPath = '/Users/zhengchaohua/Desktop/images/captcha.png'
        urllib.urlretrieve(captcha_img, localPath)
        captcha_value = raw_input('查看captcha.png,有验证码请输入:')
        formdata = {
                    '__VIEWSTATE'           : viewState,
                    '__VIEWSTATEGENERATOR'  : viewStateGenerator,
                    '__EVENTVALIDATION'     : eventValidation,
                    'txtUserName'           : 'dawnhome',
                    'txtPassword'           : 'mima0125',
                    'CheckBox1'             : 'on',
                    'ImageButton1.x'        :'38',
                    'ImageButton1.y'        :'33',
                    'txtYzmCode'            : captcha_value
                   }
        print("----------登录中----------")
        return [FormRequest.from_response(
            response,
            meta        ={'cookiejar': response.meta['cookiejar']},
            headers     =self.headers,
            formdata    =formdata,
            callback    = self.after_login
        )]

    def after_login(self,response,page = 1):
        print("----------完成登录----------")
        # if response.meta != None :
        #     if response.meta['page'] != None:
        #         print('123')
        yield FormRequest(
                self.base_url + '/Web/ashx_/PaperSearch.ashx',
                headers=self.headers,
                meta = {"cookiejar":response.meta["cookiejar"]},
                formdata = {
                            'cid' : '1',
                            'gr'  : '高三级',
                            'cty' : '高考真题',
                            'page': str(page)
                           },
                callback = self.parse_paper_list,
                # dont_filter=True
        )



    def parse_paper_list(self,response):
        # papers = html.fromstring(response.body)
        js = json.loads(response.body)
        xml_string = html.fromstring(js['data'])
        papers = xml_string.xpath("//a[@class='goto']/@href")
        # for paper in papers:
        #     if 'PaperCenter' in paper:
        #         continue
        #     else:
        #         yield Request(
        #             self.base_url+ '/' + paper,
        #             callback=self.parse_exercise_list,
        #             dont_filter=True
        #         )

        page_string  = html.fromstring(js['pager'])
        current_page = page_string.xpath("//a[1]/text()")[0]
        current_page = '总34条记录,页次:4/14页'
        total_page   = re.sub("\D","",current_page)[0]
        print(total_page)

    def parse_exercise_list(self, response):
        # print(response.body)
        title = response.xpath('//title/text()').extract()[0].encode('utf-8');
        paper = {
            'title': title
        }
        yield paper
