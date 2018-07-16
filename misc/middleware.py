# -*- coding: utf-8 -*-
from proxy import PROXIES, FREE_PROXIES
from agents import AGENTS
import logging as log
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import time
import random


class CustomHttpProxyFromMysqlMiddleware(object):
    proxies = FREE_PROXIES

    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy(request):
            p = random.choice(self.proxies)
            try:
                request.meta['proxy'] = "http://%s" % p['ip_port']
                print('current proxy:')
                print(request.meta['proxy'])
            except Exception, e:
                #log.msg("Exception %s" % e, _level=log.CRITICAL)
                log.critical("Exception %s" % e)

    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        #if "depth" in request.meta and int(request.meta['depth']) <= 2:
        #    return False
        #i = random.randint(1, 10)
        #return i <= 2
        return True


class CustomHttpProxyMiddleware(object):

    def process_request(self, request, spider):
        # TODO implement complex proxy providing algorithm
        if self.use_proxy(request):
            p = random.choice(PROXIES)
            try:
                request.meta['proxy'] = "http://%s" % p['ip_port']
            except Exception, e:
                #log.msg("Exception %s" % e, _level=log.CRITICAL)
                log.critical("Exception %s" % e)

    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        #if "depth" in request.meta and int(request.meta['depth']) <= 2:
        #    return False
        #i = random.randint(1, 10)
        #return i <= 2
        return True


class CustomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent


#写一个中间件来处理图片下载的防盗链：
class DownloadImageMiddleware(object):
    def process_request(self, request, spider):
        '''
        设置headers和切换请求头
        :param request: 请求体
        :param spider: spider对象
        :return: None
        '''
        referer = request.meta.get('referer', None)
        if referer:
            request.headers['referer'] = referer


js = """
function scrollToBottom() {

    var Height = document.body.clientHeight,  //文本高度
        screenHeight = window.innerHeight,  //屏幕高度
        INTERVAL = 100,  // 滚动动作之间的间隔时间
        delta = 500,  //每次滚动距离
        curScrollTop = 0;    //当前window.scrollTop 值

    var scroll = function () {
        curScrollTop = document.body.scrollTop;
        window.scrollTo(0,curScrollTop + delta);
    };

    var timer = setInterval(function () {
        var curHeight = curScrollTop + screenHeight;
        if (curHeight >= Height){   //滚动到页面底部时，结束滚动
            clearInterval(timer);
        }
        scroll();
    }, INTERVAL)
}
scrollToBottom()
"""
class PhantomJSMiddleware(object):
    pass
    # def process_request(self, request, spider):
        # if spider.name == 'phantomjs' :#and request.meta.has_key('PhantomJS')
        #     print('-------------------')
        #     chrome_options = Options()
        #     chrome_options.add_argument('--headless')
        #     chrome_options.add_argument('--disable-gpu')
        #     driver  = webdriver.Chrome()
        #     content = driver.get(request.url)
        #     return HtmlResponse(request.url,encoding='utf-8',body=content,request=request)
