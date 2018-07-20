# -*- coding: utf-8 -*-

import re
import sys
import json
import time
import redis
import scrapy
import urllib
from lxml                import html
from bs4                 import BeautifulSoup
from scrapy.selector     import Selector
from scrapy.http.cookies import CookieJar
from scrapy.http         import Request , FormRequest

reload(sys)
sys.setdefaultencoding("utf-8")
# 实例化一个cookiejar对象
cookie_jar = CookieJar()

local_redis = redis.Redis(host='127.0.0.1',port=6379)

class ZxlsSpider(scrapy.Spider):
    name = 'zxls'
    allowed_domains = ['zujuan.zxls.com']
    start_urls = [
        'http://zujuan.zxls.com/Web/ashx_/PaperSearch.ashx',
        'http://zujuan.zxls.com/Web/ashx_/PaperSearch.ashx',
        'http://zujuan.zxls.com/PaperLatest.aspx',
        'http://zujuan.zxls.com/PaperList.aspx',
    ]

    site = '13'

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
        'ASP.NET_SessionId':'0smgh4bxmkrkisx0fij25ezh',
        'kemu':'1'
    }
    # cookies = {}
    def start_requests(self):
        return [Request(
            self.base_url + '/Login.aspx?ReturnUrl=/Index.aspx',
            cookies  = {'kemu':'1'},
            meta     = {'cookiejar' : 1},
            callback = self.login
        )]

    def login(self,response):
        viewState           = Selector(response).xpath('//input[@name="__VIEWSTATE"]/@value').extract()[0]
        viewStateGenerator  = Selector(response).xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value').extract()[0]
        eventValidation     = Selector(response).xpath('//input[@name="__EVENTVALIDATION"]/@value').extract()[0]
        captcha_img         = self.base_url + '/' + Selector(response).xpath("//img[@id='imgcode']/@src").extract()[0]
        localPath           = '/Users/zhengchaohua/Desktop/Media/Images/captcha.png'
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
        yield FormRequest(
                self.base_url + '/Web/ashx_/PaperSearch.ashx',
                headers=self.headers,
                cookies=self.cookies,
                meta = {"cookiejar":response.meta["cookiejar"]},
                formdata = {
                            'cid' : '1',
                            'gr'  : '高三级',
                            # 'cty' : '高考真题',
                            'page': '1',
                            'rows': '10',
                            'pyear': '2018',
                            # 'pn': '2015届高考《步步高》一轮复习配套题库：第22课时 经济建设的发展和曲折'
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
                    # 'cty' : '高考真题',
                    'page': str(next_page),
                    'rows': '10',
                    'pyear': '2018',
                    # 'pn': '2015届高考《步步高》一轮复习配套题库：第22课时 经济建设的发展和曲折'
                },
                callback = self.parse_paper_list,
                dont_filter=True
            )

    def parse_exercise_list(self, response):
        url          = response.url
        title        = response.xpath("//div[@class='sjbt']/h1/text()").extract_first()
        subject      = self.cid[1]
        grade        = response.xpath("//div[@class='xiaobiaoti']/span[1]/text()").extract_first().replace(u'适用年级：' , '').replace(u'级','')
        type         = response.xpath("//div[@class='xiaobiaoti']/span[2]/text()").extract_first().replace(u'试卷类型：' , '')
        year         = response.xpath("//div[@class='xiaobiaoti']/span[4]/text()").extract_first().replace(u'试卷年份：' , '').replace(u'年','')
        exercise_num = response.xpath("//div[@class='xiaobiaoti']/span[5]/text()").extract_first().replace(u'题数：'    , '')
        views        = response.xpath("//div[@class='xiaobiaoti']/span[6]/text()").extract_first().replace(u'浏览数：'  , '')
        uploaded_at  = response.meta['year']
        paper = {
            'site_id'       : self.site,
            'url'           : url,
            'title'         : title,
            'subject'       : subject,
            'grade'         : grade,
            'type'          : type,
            'level'         : '0',
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
            if child.name == 'p':
                local_redis.set('exercise_type',child.get_text().split('、')[-1])
            if child.name == 'div':
                tds         = child.find_all('td')
                description = str(tds[1])
                imgs        = Selector(text=str(child)).xpath('//img/@src').extract()
                is_wrong    = 0
                description_imgs = {}
                if len(imgs) > 0:
                    for img in imgs:
                        if str(img).startswith('../'):
                            imgUlr =  str(img).split('..')[-1]
                        if str(img).startswith('data:'):
                            continue
                        else:
                            imgUlr = str(img)
                        description_imgs[img] = self.base_url+imgUlr
                options     = child.find_all('td',attrs={'class':'sstd'})
                if len(options) == 0:
                    options = child.find_all('td', attrs={'class': 'ddtd'})
                if local_redis['exercise_type'] == '单选题':
                    if len(options) < 1:
                        is_wrong = 1
                options_string = []
                for index,option in enumerate(options):
                    options_string.append(str(option).split('．')[-1].replace(u'</td>',''))
                options   = json.dumps(options_string,ensure_ascii=False) # 不转码 存储到数据库为中文
                source_id = child.find_all('input')[0]['value']
                sort += 1
                exercise = {
                    'subject'          : subject,
                    'site_id'          : self.site,
                    'grade'            : grade,
                    'source_id'        : source_id,
                    'type'             : local_redis['exercise_type'],
                    'description'      : description,
                    'options'          : options,
                    'answer_img'       : None,
                    'method_img'       : None,
                    'url'              : None,
                    'sort'             : sort,
                    'paper'            : paper,
                    'is_wrong'         : is_wrong,
                    'description_imgs' : description_imgs,
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
        points     = xml_string.xpath(u"//p[contains(text(),'【知')]/text()")[0].split('】')[-1].split('；')
        points_list= []
        for point in points:
            points_list.append(point)
        exercise['points']        = json.dumps(points_list,ensure_ascii=False) # 不转码 存储到数据库为中文
        exercise['degree']        = xml_string.xpath(u"//p[contains(text(),'【难')]/text()")[0].split('】')[-1]
        methods     = xml_string.xpath(u"//p[contains(text(),'【解')]/following-sibling::p[1]/text()")
        if len(methods) > 0:
            exercise['method'] = ''
            for method in methods:
                if method == None:
                    continue
                exercise['method'] += method
        else:
            exercise['method'] = None
        if exercise['type'] == '单选题':
            exercise['answer']     = xml_string.xpath(u"//p[contains(text(),'【答')]/text()")[0].split('】')[-1]
        else:
            answers = xml_string.xpath(u"//p[contains(text(),'【答')]/following-sibling::p[1]/text()")
            if len(answers) > 0:
                exercise['answer'] = ''
                for answer in answers:
                    if answer == None:
                        continue
                    exercise['answer'] += answer
            else:
                exercise['answer'] = None
        yield exercise

