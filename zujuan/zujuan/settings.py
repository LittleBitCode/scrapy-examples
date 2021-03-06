# -*- coding: utf-8 -*-

# Scrapy settings for zujuan project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import sys
import os
from os.path import dirname

path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(path)

from misc.log import *




BOT_NAME         = 'zujuan'

SPIDER_MODULES   = ['zujuan.spiders']
NEWSPIDER_MODULE = 'zujuan.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'zujuan (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY  = False

# Disable cookies (enabled by default)
# 自动传递cookies与打印cookies设置
COOKIES_ENABLED = True
# COOKIES_DEBUG   = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
#     'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'zujuan.middlewares.ZujuanSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'misc.middleware.PhantomJSMiddleware' : 1,
    # 'misc.middleware.CustomHttpProxyFromMysqlMiddleware' : 400,
    # 'misc.middleware.CustomUserAgentMiddleware'          : 401,
#     'misc.middleware.DownloadImageMiddleware'            : 543,
#     'scrapy_splash.SplashCookiesMiddleware': 723,
#     'scrapy_splash.SplashMiddleware': 725,
#     'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# 优先级 1-1000 越小优先级越高
ITEM_PIPELINES = {
    'zujuan.pipelines.DownloadImagesPipeline': 1, #本地保存图片
    'zujuan.pipelines.ocrPipeline'           : 2, #图片文字识别
    'zujuan.pipelines.ZujuanPipeline'        : 3, #保存试卷试题
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# 自动限速（AutoTrottle）下载图片时使用
# 值得注意的是，启用AutoThrottle扩展时，仍然受到DOWNLOAD_DELAY（下载延迟）
# 和CONCURRENT_REQUESTS_PER_DOMAIN（对单个网站进行并发请求的最大值）
# 以及CONCURRENT_REQUESTS_PER_IP（对单个IP进行并发请求的最大值）的约束。
# 启用AutoThrottle扩展
# AUTOTHROTTLE_ENABLED = True
# 初始下载延迟(单位:秒)
# AUTOTHROTTLE_START_DELAY = 5
# 在高延迟情况下最大的下载延迟(单位秒)
# AUTOTHROTTLE_MAX_DELAY = 60
# 设置 Scrapy应该与远程网站并行发送的平均请求数, 目前是以1个并发请求数
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# 启用AutoThrottle调试模式
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 本地测试数据库
MYSQL_HOST    = "127.0.0.1"
MYSQL_USER    = "root"
MYSQL_PASSWD  = "123456"
MYSQL_PORT    = 3306
MYSQL_CHARSET = "utf8"
MYSQL_DBNAME  = "spider"

# 威科姆中转数据库
# MYSQL_HOST    = "192.168.151.230"
# MYSQL_USER    = "crawl"
# MYSQL_PASSWD  = "E^h0O%5QcLWWacWUzGd46HIXg"
# MYSQL_PORT    = 3306
# MYSQL_CHARSET = "utf8"
# MYSQL_DBNAME  = "spider"

# SPLASH_URL='http://127.0.0.1:8050'
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
#工程根目录
#/Users/macbookpro/Desktop/MyProject/Examples/zujuan/zujuan
project_dir   = os.path.dirname(__file__)
IMAGES_STORE  = os.path.join(project_dir, '')
# 该字段的值为ImageItem中定义的存储图片链接的image_urls字段
#IMAGES_URLS_FIELD='image_urls'
# 该字段的值为ImageItem中定义的存储图片信息的images字段
#IMAGES_RESULT_FIELD='images'
# 避免下载最近90天已经下载过的文件内容,单位:天(可选)
# IMAGES_EXPIRES    = 90
# 设置图片缩略图(可选)
# IMAGES_THUMBS = {
#     'small' : (50, 50),
#     'big'   : (250, 250),
# }
# 图片过滤器，最小高度和宽度，低于此尺寸不下载(可选)
#IMAGES_MIN_HEIGHT = 100
#IMAGES_MIN_WIDTH  = 100
# 是否允许重定向(可选)
# MEDIA_ALLOW_REDIRECTS = True
# BAIDUAPI = {
#     'APP_ID'     : '10733367',
#     'API_KEY'    : 'WYAFwtoMQoapxd4poaDm7hB2',
#     'SECRET_KEY' : 'AGBBRZ8QKGrN1vaMeDosHlLWY7GaqzNA',
# }
BAIDUAPI = {
    'APP_ID'     : '11532440',
    'API_KEY'    : 'hhW4gM2CAZdsUqjUyIA1WxZF',
    'SECRET_KEY' : 'Thh51ejbCG4u1eV1CUWa6WYW7blsrsX5',
}