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

    def start_requests(self):
        return [Request(self.base_url + '/Login.aspx',cookies={'kemu':'1'}, meta = {'cookiejar' : 1},callback = self.login)]

    def login(self,response):
        viewState           = Selector(response).xpath('//input[@name="__VIEWSTATE"]/@value').extract()[0]
        viewStateGenerator  = Selector(response).xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').extract()[0]
        eventValidation     = Selector(response).xpath('//input[@name="__EVENTVALIDATION"]/@value').extract()[0]
        captcha_img         = 'http://zujuan.zxls.com/CheckCode.aspx'
        localPath           = '/Users/zhengchaohua/Desktop/images/captcha.png'
        urllib.urlretrieve(captcha_img, localPath)
        captcha_value       = raw_input('查看captcha.png,有验证码请输入:')
        formdata = {
                    '__VIEWSTATE'           : viewState,
                    '__VIEWSTATEGENERATOR'  : viewStateGenerator,
                    '__EVENTVALIDATION'     : eventValidation,
                    'txtUserName'           : 'dawnhome',
                    'txtPassword'           : 'mima0125',
                    'CheckBox1'             : 'on',
                    'ImageButton1.x'        : '125',
                    'ImageButton1.y'        : '17',
                    'txtYzmCode'            : captcha_value
                   }
        return [FormRequest.from_response(
            response,
            meta        = {'cookiejar': response.meta['cookiejar']},
            headers     = self.headers,
            formdata    = formdata,
            callback    = self.after_login
        )]


    def after_login(self,response):
        # 请求Cookie
        Cookie2 = response.request.headers.getlist('Cookie')
        # 响应Cookie
        Cookie  = response.headers.getlist('Set-Cookie')
        print(u'登录时携带请求的Cookies：', Cookie2)
        return
        yield FormRequest(
                self.base_url + '/Web/ashx_/PaperSearch.ashx',
                headers=self.headers,
                meta = {"cookiejar":response.meta["cookiejar"]},
                formdata = {
                            'cid' : '1',
                            'gr'  : '高三级',
                            'cty' : '高考真题',
                            'page': '1',
                            'rows': '10'
                           },
                callback = self.parse_paper_list,
                # dont_filter=True
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
                    meta     ={'year':year,"cookiejar":response.meta["cookiejar"]},
                    callback =self.parse_exercise_list,
                    # dont_filter=True
                )
        # 下一页
        page_string  = html.fromstring(js['pager'])
        current_page = page_string.xpath("//a[@class='change']/text()")[0]
        total_page   = int( int(js['total']) / 10) + 1
        next_page    = int(current_page) + 1
        # if next_page <= total_page:
        #     yield FormRequest(
        #         self.base_url + '/Web/ashx_/PaperSearch.ashx',
        #         headers=self.headers,
        #         meta={"cookiejar": response.meta["cookiejar"]},
        #         formdata={
        #             'cid' : '1',
        #             'gr'  : '高三级',
        #             'cty' : '高考真题',
        #             'page': str(next_page),
        #             'rows': '10'
        #         },
        #         callback=self.parse_paper_list,
        #         # dont_filter=True
        #     )

    def parse_exercise_list(self, response):
        url          = response.url
        title        = response.xpath("//div[@class='sjbt']/h1/text()").extract_first()
        subject      = self.cid[1]
        grade        = response.xpath("//div[@class='xiaobiaoti']/span[1]/text()").extract_first().replace(u'适用年级：', '')
        type         = response.xpath("//div[@class='xiaobiaoti']/span[2]/text()").extract_first().replace(u'试卷类型：', '')
        year         = response.xpath("//div[@class='xiaobiaoti']/span[4]/text()").extract_first().replace(u'试卷年份：', '').replace(u'年','')
        exercise_num = response.xpath("//div[@class='xiaobiaoti']/span[5]/text()").extract_first().replace(u'题数：', '')
        views        = response.xpath("//div[@class='xiaobiaoti']/span[6]/text()").extract_first().replace(u'浏览数：', '')
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
        #题型
        # exercise_types = response.xpath("//div[@id='subjectList']/p/text()").extract()
        exercise_types = response.xpath("//div[@id='subjectList']/p")
        # for index,exercise_type in enumerate(exercise_types):
        # exercise_type = response.xpath("//div[@id='subjectList']/p/text()").extract()[index]
        exercises  = response.xpath(".//div[@class='subject']")
        sort = 0
        for index,exercise in enumerate(exercises):
            if exercise != None:
                description = exercise.xpath(".//tr[1]/td[2]").extract_first()
                detail      = exercise.xpath(".//tr[1]/td[2]/h3/text()").extract_first()
                options     = json.dumps(exercise.xpath(".//td[@class='sstd']/text()").extract())
                source_id   = exercise.xpath("//input[@class='ppids']/@value").extract()[index]
                if detail != None or options != None:
                    sort += 1
                    exercise = {
                        'subject'      : subject,
                        'degree'       : None,
                        'source_id'    : source_id,
                        'type'         : None,
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
                            self.base_url+'/Web/ashx_/ProblemAttend.ashx?id='+source_id,
                            meta     = {'exercise':exercise,"cookiejar":response.meta["cookiejar"]},
                            callback = self.parse_exercise_detail
                        )


    def parse_exercise_detail(self,response):
        # http://zujuan.zxls.com/Web/ashx_/ProblemAttend.ashx?id=   问题解析
        print(response.url)
        return